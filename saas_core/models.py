from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

# ============================================================================
# 1. SAAS PRICING & SUBSCRIPTION ENGINE
# ============================================================================
class SubscriptionPlan(models.Model):
    """
    SaaS Pricing Tiers (e.g., Free Trial, Starter, Pro, Enterprise)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    
    # Global & Local Pricing
    monthly_price_bdt = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    monthly_price_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Core Limits
    max_users = models.IntegerField(default=1, help_text="Number of staff accounts allowed")
    max_domains = models.IntegerField(default=1, help_text="Number of custom domains allowed")
    max_storage_gb = models.DecimalField(max_digits=6, decimal_places=2, default=1.00)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (৳{self.monthly_price_bdt})"


# ============================================================================
# 2. WORKSPACE (THE TENANT CORE)
# ============================================================================
class Workspace(models.Model):
    """
    The central hub for a business. Every invoice, lead, and employee 
    will be linked to a Workspace ID for total data isolation.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='owned_workspaces')
    
    company_name = models.CharField(max_length=100)
    subdomain = models.SlugField(unique=True, help_text="e.g., ecompilot.scalexerp.com")
    
    # Branding per workspace
    logo = models.ImageField(upload_to='workspace/logos/', blank=True, null=True)
    primary_color = models.CharField(max_length=20, default="#4338ca")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name


# ============================================================================
# 3. CUSTOM DOMAIN ROUTING (WaaS Engine)
# ============================================================================
class CustomDomain(models.Model):
    """
    Cloudflare DNS ready Custom Domain routing system.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='domains')
    
    domain_name = models.CharField(max_length=100, unique=True, help_text="e.g., www.client-brand.com")
    is_primary = models.BooleanField(default=False)
    
    # DNS Instructions for User (System generated)
    cname_target = models.CharField(max_length=150, default="shops.scalexerp.com", help_text="What user needs to point to")
    verification_txt_name = models.CharField(max_length=100, blank=True, null=True)
    verification_txt_value = models.CharField(max_length=255, blank=True, null=True)
    
    # Cloudflare / API Status
    cloudflare_hostname_id = models.CharField(max_length=100, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    ssl_status = models.CharField(max_length=20, choices=[('PENDING', 'Pending'), ('ACTIVE', 'Active')], default='PENDING')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.domain_name


# ============================================================================
# 4. WORKSPACE SUBSCRIPTION TRACKER
# ============================================================================
class WorkspaceSubscription(models.Model):
    """
    Tracks the financial health and active plan of a workspace.
    """
    STATUS_CHOICES = [
        ('TRIAL', 'Trial Period'),
        ('ACTIVE', 'Active & Paid'),
        ('PAST_DUE', 'Payment Failed / Retrying'),
        ('SUSPENDED', 'Access Suspended'),
    ]
    
    workspace = models.OneToOneField(Workspace, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TRIAL')
    current_period_end = models.DateTimeField()
    
    # Usage Tracking (Meters)
    current_storage_used_mb = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    updated_at = models.DateTimeField(auto_now=True)

    def is_valid(self):
        return self.status in ['TRIAL', 'ACTIVE'] and self.current_period_end > timezone.now()

    def __str__(self):
        return f"{self.workspace.company_name} - {self.plan.name} ({self.status})"
    


# ============================================================================
# 5. APP STORE & DYNAMIC MENU ENGINE
# ============================================================================
class SaaSAppModule(models.Model):
    """
    আপনার সফটওয়্যারের প্রতিটি সেকশন (HR, CRM, POS) আলাদা অ্যাপ হিসেবে কাজ করবে।
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, help_text="e.g., Advanced CRM")
    module_code = models.CharField(max_length=50, unique=True, help_text="e.g., crm (Controls Menu Visibility)")
    icon_class = models.CharField(max_length=50, default="fas fa-box", help_text="FontAwesome or SVG class")
    
    description = models.TextField(blank=True)
    monthly_fee_bdt = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    is_core_module = models.BooleanField(default=False, help_text="If True, it is free and always visible")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class TenantActiveModule(models.Model):
    """
    ইউজার App Store থেকে কোন কোন মডিউল কিনেছে তার ট্র্যাকিং।
    এটার ওপর ভিত্তি করেই ড্যাশবোর্ডের মেনু শো/হাইড হবে!
    """
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='active_modules')
    module = models.ForeignKey(SaaSAppModule, on_delete=models.PROTECT)
    purchased_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('workspace', 'module')

    def __str__(self):
        return f"{self.workspace.company_name} -> {self.module.name}"
    
# ============================================================================
# 6. GLOBAL MASTER DATA (Currencies & Regions)
# ============================================================================
class GlobalCurrency(models.Model):
    """
    Master list of world currencies. Controlled only by the Super Admin.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=3, unique=True, help_text="e.g., USD, BDT, EUR")
    name = models.CharField(max_length=50, help_text="e.g., US Dollar, Bangladeshi Taka")
    symbol = models.CharField(max_length=10, help_text="e.g., $, ৳, €")
    
    # Optional: For future multi-currency automated conversions
    exchange_rate_to_usd = models.DecimalField(max_digits=10, decimal_places=4, default=1.0000)
    
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} ({self.symbol})"


# ============================================================================
# 7. WORKSPACE LOCALIZATION & SETTINGS (The Tenant config)
# ============================================================================
class WorkspaceSettings(models.Model):
    """
    Specific operational settings for a tenant (Address, Currency, Timezone).
    This drives the symbols on their invoices and the timezone of their reports.
    """
    workspace = models.OneToOneField(Workspace, on_delete=models.CASCADE, related_name='localization')
    
    # Financial & Legal
    base_currency = models.ForeignKey(GlobalCurrency, on_delete=models.SET_NULL, null=True, blank=True)
    tax_id_or_vat = models.CharField(max_length=50, blank=True, help_text="Company VAT/BIN/EIN Number for invoices")
    
    # Global Address System
    country = models.CharField(max_length=100, default='Bangladesh')
    state_or_division = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    full_address = models.TextField(blank=True, help_text="Street address for official documents")
    
    # Regional Formatting
    timezone = models.CharField(max_length=50, default='Asia/Dhaka')
    date_format = models.CharField(max_length=20, choices=[
        ('YYYY-MM-DD', 'YYYY-MM-DD (e.g., 2026-12-31)'), 
        ('DD-MM-YYYY', 'DD-MM-YYYY (e.g., 31-12-2026)'), 
        ('MM/DD/YYYY', 'MM/DD/YYYY (e.g., 12/31/2026)')
    ], default='DD-MM-YYYY')

    def __str__(self):
        return f"Settings: {self.workspace.company_name}"


# ============================================================================
# 8. SYSTEM HEALTH & ERROR TRACKING (APM ENGINE)
# ============================================================================
class SystemErrorLog(models.Model):
    """
    Catch-all table for any system crashes, bugs, or unhandled exceptions.
    Tracks exact line numbers, memory usage, and execution time.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Bug Details
    error_type = models.CharField(max_length=255)
    error_message = models.TextField()
    file_name = models.CharField(max_length=255)
    line_number = models.IntegerField(null=True, blank=True)
    traceback_data = models.TextField(help_text="Full technical stack trace")
    
    # Performance & Request Context
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    execution_time_ms = models.FloatField(default=0.0, help_text="Time taken before crash (in ms)")
    memory_usage_mb = models.FloatField(default=0.0, help_text="Peak memory usage (in MB)")
    
    # User Context (If any)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    workspace = models.ForeignKey('Workspace', on_delete=models.SET_NULL, null=True, blank=True)
    
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.error_type} in {self.file_name} at line {self.line_number}"


# ============================================================================
# 9. SUPER-ADMIN NOTIFICATION SYSTEM
# ============================================================================
class AdminNotification(models.Model):
    """
    Alerts superusers instantly when a critical error occurs.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True, null=True, help_text="Link to the error log")
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    

# ============================================================================
# 10. SYSTEM HELP & TUTORIALS (Dynamic Video Embeds)
# ============================================================================
class PageTutorial(models.Model):
    """
    অ্যাডমিন প্যানেল থেকে নির্দিষ্ট পেজের জন্য ভিডিও টিউটোরিয়াল সেট করার মডেল।
    """
    page_identifier = models.CharField(max_length=50, unique=True, help_text="e.g., 'add_client', 'create_invoice'")
    title = models.CharField(max_length=150, default="How to use this page")
    video_embed_url = models.URLField(help_text="YouTube Embed URL (e.g., https://www.youtube.com/embed/dQw4w9WgXcQ)")
    description = models.TextField(blank=True, help_text="Short instructions for the user.")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Tutorial: {self.page_identifier}"