import sys
import traceback
import time
import tracemalloc
from django.http import Http404
from django.conf import settings
from .models import Workspace, CustomDomain, SystemErrorLog, AdminNotification
from django.contrib.auth import get_user_model

User = get_user_model()
class TenantMiddleware:
    """
    Identifies the Tenant (Workspace) from the request URL.
    Routes custom domains or subdomains automatically.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0]  # Remove port if running locally
        main_domain = getattr(settings, 'MAIN_DOMAIN', '127.0.0.1')

        request.workspace = None
        request.is_custom_domain = False

        # Safe user access: AuthenticationMiddleware should run earlier, but guard anyway
        user = getattr(request, 'user', None)

        if host == main_domain or host == 'localhost' or host in ('127.0.0.1', '::1'):
            # Local development fallback
            if user and getattr(user, 'is_authenticated', False):
                # 1. If user has workspace_id, prefer that
                if getattr(user, 'workspace_id', None):
                    try:
                        request.workspace = Workspace.objects.get(id=user.workspace_id)
                    except Workspace.DoesNotExist:
                        request.workspace = None

                # 2. If still none, take first workspace owned by the user
                if not request.workspace:
                    request.workspace = Workspace.objects.filter(owner=user).first()

                # 3. Superuser fallback: first workspace in DB
                if not request.workspace and getattr(user, 'is_superuser', False):
                    request.workspace = Workspace.objects.first()
        else:
            # =================================================================
            # PRODUCTION ROUTING (Custom Domain & Subdomain)
            # =================================================================
            try:
                domain_obj = CustomDomain.objects.get(domain_name=host, is_verified=True)
                request.workspace = domain_obj.workspace
                request.is_custom_domain = True
            except CustomDomain.DoesNotExist:
                if host.endswith(main_domain):
                    subdomain = host.replace(f'.{main_domain}', '')
                    try:
                        request.workspace = Workspace.objects.get(subdomain=subdomain, is_active=True)
                    except Workspace.DoesNotExist:
                        raise Http404("Workspace Suspended or Not Found")
                else:
                    raise Http404("Invalid Domain Configuration")

        response = self.get_response(request)
        return response
    




class AdvancedErrorTrackingMiddleware:
    """
    Tracks application crashes, logs line numbers, calculates execution time,
    measures memory usage, and notifies superusers globally.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Start tracking time and memory
        request._start_time = time.time()
        tracemalloc.start()
        
        response = self.get_response(request)
        
        # Stop memory tracking for successful requests
        if tracemalloc.is_tracing():
            tracemalloc.stop()
            
        return response

    def process_exception(self, request, exception):
        """
        This method is ONLY triggered when a Django view throws an unhandled error/500 crash.
        """
        # 2. Stop tracking & Calculate metrics
        execution_time = (time.time() - getattr(request, '_start_time', time.time())) * 1000 # in milliseconds
        
        memory_mb = 0.0
        if tracemalloc.is_tracing():
            current, peak = tracemalloc.get_traced_memory()
            memory_mb = peak / (1024 * 1024) # Convert bytes to MB
            tracemalloc.stop()

        # 3. Extract exact Error location and Line Number
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb_list = traceback.extract_tb(exc_traceback)
        
        if tb_list:
            filename, line_number, func_name, text = tb_list[-1] # -1 means the exact crash point
        else:
            filename, line_number = "Unknown", 0
            
        traceback_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))

        # 4. Save to Database
        workspace = getattr(request, 'workspace', None)
        user = request.user if request.user.is_authenticated else None

        error_log = SystemErrorLog.objects.create(
            error_type=exc_type.__name__,
            error_message=str(exc_value),
            file_name=filename,
            line_number=line_number,
            traceback_data=traceback_str,
            path=request.path,
            method=request.method,
            execution_time_ms=round(execution_time, 2),
            memory_usage_mb=round(memory_mb, 4),
            user=user,
            workspace=workspace
        )

        # 5. Blast Notifications to all Superusers (The FBI Alert!)
        superusers = User.objects.filter(is_superuser=True)
        notifications = [
            AdminNotification(
                user=admin,
                title=f"🚨 CRITICAL SYSTEM CRASH: {exc_type.__name__}",
                message=f"Crash in {filename} at line {line_number}. Path: {request.path}",
                link=f"/admin/saas_core/systemerrorlog/{error_log.id}/change/"
            ) for admin in superusers
        ]
        AdminNotification.objects.bulk_create(notifications)

        return None # Return None lets Django proceed with the default 500 error page