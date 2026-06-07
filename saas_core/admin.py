from django.contrib import admin
from .models import (PageTutorial, SaaSAppModule, SubscriptionPlan, Workspace, CustomDomain, WorkspaceSubscription, 
    WorkspaceSubscription ,SaaSAppModule, TenantActiveModule, SystemErrorLog, AdminNotification)

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'monthly_price_bdt', 'monthly_price_usd', 'max_domains', 'is_active')
    prepopulated_fields = {'slug': ('name',)} # নামের উপর ভিত্তি করে অটো স্লাগ হবে

@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'subdomain', 'owner', 'is_active', 'created_at')
    search_fields = ('company_name', 'subdomain', 'owner__email')

@admin.register(WorkspaceSubscription)
class WorkspaceSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('workspace', 'plan', 'status', 'current_period_end')
    list_filter = ('status', 'plan')

@admin.register(CustomDomain)
class CustomDomainAdmin(admin.ModelAdmin):
    list_display = ('domain_name', 'workspace', 'is_verified', 'ssl_status')
    list_filter = ('is_verified', 'ssl_status')

# ==========================================================
# APP STORE MODULES REGISTRATION

@admin.register(SaaSAppModule)
class SaaSAppModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'module_code', 'monthly_fee_bdt', 'is_core_module', 'is_active')
    search_fields = ('name', 'module_code')
    list_filter = ('is_core_module', 'is_active')

@admin.register(TenantActiveModule)
class TenantActiveModuleAdmin(admin.ModelAdmin):
    list_display = ('workspace', 'module', 'purchased_at')
    list_filter = ('module',)
    search_fields = ('workspace__company_name',)

@admin.register(SystemErrorLog)
class SystemErrorLogAdmin(admin.ModelAdmin):
    list_display = ('error_type', 'file_name', 'line_number', 'execution_time_ms', 'memory_usage_mb', 'created_at', 'is_resolved')
    list_filter = ('is_resolved', 'error_type', 'created_at')
    search_fields = ('error_message', 'file_name')
    readonly_fields = ('traceback_data',) # কেউ যেন কোড এডিট করতে না পারে

@admin.register(AdminNotification)
class AdminNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_read', 'created_at')
    list_filter = ('is_read',)

# ==========================================================
# SYSTEM HELP & TUTORIALS REGISTRATION
# ==========================================================
@admin.register(PageTutorial)
class PageTutorialAdmin(admin.ModelAdmin):
    list_display = ('title', 'page_identifier', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'page_identifier')