from django.contrib import admin
from .models import CustomUser, Role, UserProfile, UserDeviceTracker, SecurityAuditLog

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'get_full_name', 'role', 'is_active', 'is_staff')
    search_fields = ('email', 'phone_number')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'role')
    ordering = ('email',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone_number', 'verification_type', 'kyc_verified')
    search_fields = ('user__email', 'full_name', 'phone_number')
    list_filter = ('verification_type', 'kyc_verified', 'is_pro_badge')

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')

admin.site.register(UserDeviceTracker)
admin.site.register(SecurityAuditLog)