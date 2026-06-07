from .models import SaaSAppModule, TenantActiveModule, AdminNotification, SystemErrorLog
from django.urls import reverse

def tenant_global_data(request):
    """
    Provides workspace & menu context to templates. Returns an empty dict
    for anonymous users or when no workspace is resolved.
    """
    if not getattr(request, 'user', None) or not request.user.is_authenticated or not hasattr(request, 'workspace') or not request.workspace:
        return {}

    workspace = request.workspace

    # 1. Core modules (free/core)
    core_modules = SaaSAppModule.objects.filter(is_core_module=True, is_active=True)

    # 2. Purchased / activated modules for this workspace
    purchased_ids = TenantActiveModule.objects.filter(workspace=workspace).values_list('module_id', flat=True)
    premium_modules = SaaSAppModule.objects.filter(id__in=purchased_ids, is_active=True)

    # Combine them
    all_modules = list(core_modules) + list(premium_modules)

    # Build menu (use reverse for known routes and include '/saas/' prefix)
    try:
        dashboard_url = reverse('tenant_dashboard')
    except Exception:
        dashboard_url = '/saas/dashboard/'

    dynamic_menu = [{"label": "Dashboard", "icon": "fa-solid fa-house", "url": dashboard_url}]
    for mod in all_modules:
        # per-module route may live under /saas/app/<module>/ — ensure prefix
        dynamic_menu.append({
            "label": mod.name,
            "icon": mod.icon_class,
            "url": f"/saas/app/{mod.module_code}/"
        })

    try:
        app_store_url = reverse('app_store')
    except Exception:
        app_store_url = '/saas/app-store/'
    dynamic_menu.append({"label": "App Store", "icon": "fa-solid fa-store", "url": app_store_url})

    # Notifications (most recent unread)
    unread_notifications = AdminNotification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]
    unread_count = AdminNotification.objects.filter(user=request.user, is_read=False).count()

    return {
        'current_workspace': workspace,
        'dynamic_menu': dynamic_menu,
        'primary_color': workspace.primary_color,
        'workspace_logo': workspace.logo.url if workspace.logo else None,
        'unread_notifications': unread_notifications,
        'unread_count': unread_count,
    }