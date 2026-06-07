from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import SaaSAppModule, TenantActiveModule, AdminNotification
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

@login_required
def get_dynamic_sidebar_menu(request):
    """
    Returns a dynamic JSON menu based on the user's workspace and purchased apps.
    Perfect for React/Vue or dynamic Django templates.
    """
    workspace = getattr(request, 'workspace', None)
    
    if not workspace:
        return JsonResponse({"error": "No active workspace found for this URL"}, status=403)

    # 1. Get Core/Free Modules (Always visible)
    core_modules = SaaSAppModule.objects.filter(is_core_module=True, is_active=True)
    
    # 2. Get Purchased/Premium Modules for this specific Workspace
    purchased_module_ids = TenantActiveModule.objects.filter(workspace=workspace).values_list('module_id', flat=True)
    premium_modules = SaaSAppModule.objects.filter(id__in=purchased_module_ids, is_active=True)
    
    # 3. Combine them
    all_allowed_modules = list(core_modules) + list(premium_modules)
    
    # 4. Build the JSON Menu Structure
    try:
        dashboard_url = reverse('tenant_dashboard')
    except Exception:
        dashboard_url = '/saas/dashboard/'

    menu_data = [
        {
            "label": "Dashboard",
            "icon": "fas fa-home",
            "url": dashboard_url,
            "module_code": "core"
        }
    ]
    
    for mod in all_allowed_modules:
        menu_data.append({
            "label": mod.name,
            "icon": mod.icon_class,
            "url": f"/saas/app/{mod.module_code}/", # Dynamic URL routing
            "module_code": mod.module_code
        })
        
    # Always show App Store at the bottom
    try:
        app_store_url = reverse('app_store')
    except Exception:
        app_store_url = '/saas/app-store/'

    menu_data.append({
        "label": "App Store",
        "icon": "fas fa-store",
        "url": app_store_url,
        "module_code": "store",
        "is_highlighted": True
    })

    return JsonResponse({
        "workspace_name": workspace.company_name,
        "branding_color": workspace.primary_color,
        "menu": menu_data
    })


@login_required(login_url='/admin/login/') # আপাতত অ্যাডমিন লগইন ব্যবহার করছি
def tenant_dashboard(request):
    """
    The main landing page for a workspace owner/user.
    """
    return render(request, 'dashboard.html')


from .models import SaaSAppModule, TenantActiveModule

@login_required(login_url='/admin/login/')
def app_store(request):
    """
    Displays the App Store. Shows which apps are already installed
    and which ones are available for upgrade.
    """
    workspace = getattr(request, 'workspace', None)
    
    # সিস্টেমে থাকা সব মডিউল
    all_modules = SaaSAppModule.objects.filter(is_active=True).order_by('-is_core_module', 'name')
    
    # এই ওয়ার্কস্পেসের কোন কোন মডিউল অলরেডি ইন্সটল করা আছে তার লিস্ট
    installed_module_ids = []
    if workspace:
        installed_module_ids = TenantActiveModule.objects.filter(
            workspace=workspace
        ).values_list('module_id', flat=True)
    
    context = {
        'all_modules': all_modules,
        'installed_module_ids': list(installed_module_ids),
    }
    return render(request, 'app_store.html', context)


@login_required(login_url='/admin/login/')
def read_notification(request, notification_id):
    """
    Marks a notification as read and redirects the user to the issue link.
    """
    notification = get_object_or_404(AdminNotification, id=notification_id, user=request.user)
    
    if not notification.is_read:
        notification.is_read = True
        notification.save()
        
    if notification.link:
        return redirect(notification.link)
    return redirect('tenant_dashboard')