from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import uuid

# ============================================================================
# 1. CUSTOM USER MANAGER
# ============================================================================
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

# ============================================================================
# 2. ROLE BASED ACCESS CONTROL (RBAC)
# ============================================================================
class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    permissions_matrix = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

# ============================================================================
# 3. CORE AUTHENTICATION ENGINE (Extremely Lean for Speed)
# ============================================================================
class CustomUser(AbstractUser):
    """
    Core Auth Model: Kept ultra-light for fast query execution during logins.
    """
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True,
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.'
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None 
    email = models.EmailField(unique=True, db_index=True)
    
    # System Links
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    workspace_id = models.UUIDField(null=True, blank=True, db_index=True)
    
    # Security States
    is_verified = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

# ============================================================================
# 4. MARKETPLACE & DEMOGRAPHIC PROFILE (The Facebook Approach)
# ============================================================================
class UserProfile(models.Model):
    """
    Stores massive amounts of user details for future Marketplace, Analytics, 
    and AI recommendations. Connected via OneToOneField.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    
    # Basic Info
    full_name = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, unique=True, null=True)
    avatar = models.ImageField(upload_to='users/avatars/', blank=True, null=True)
    
    # ========================================================================
    # PUBLIC BADGES & STATUS (The "Blue Tick" & "PRO" System)
    # ========================================================================
    is_verified_badge = models.BooleanField(default=False, help_text="Shows a Blue Tick (✔) next to the user's name")
    is_pro_badge = models.BooleanField(default=False, help_text="Shows a 'PRO' tag for premium subscribers")
    
    VERIFICATION_TYPES = [
        ('NONE', 'Not Verified'),
        ('IDENTITY', 'Identity Verified (Standard Blue Tick)'),
        ('BUSINESS', 'Verified Business (Gold Tick)'),
        ('GOVERNMENT', 'Government Official (Grey Tick)'),
    ]
    verification_type = models.CharField(max_length=20, choices=VERIFICATION_TYPES, default='NONE')
    
    # Demographics & KYC (Background Verification Data)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=15, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], blank=True)
    national_id_or_passport = models.CharField(max_length=50, blank=True, null=True)
    kyc_verified = models.BooleanField(default=False, help_text="True if back-office approved their KYC docs")
    
    # Location & Behavioral Data
    billing_address = models.TextField(blank=True)
    shipping_address = models.TextField(blank=True)
    country = models.CharField(max_length=50, blank=True)
    preferred_currency = models.CharField(max_length=3, default='BDT')
    preferred_language = models.CharField(max_length=10, default='en')
    
    # Dynamic Preferences (For targeting & AI)
    interests_tags = models.JSONField(default=list, blank=True, help_text="e.g. ['tech', 'fashion', 'b2b']")
    
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile: {self.user.email}"

# ============================================================================
# 5. DEVICE & TELEMETRY ENGINE (The "CIA/FBI" Tracking Level)
# ============================================================================
class UserDeviceTracker(models.Model):
    """
    Tracks every physical device and location the user logs in from.
    Crucial for identifying account sharing, fraud, and precise targeting.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='devices')
    
    # Fingerprinting
    device_id = models.CharField(max_length=255, help_text="Browser/Hardware Fingerprint Hash", db_index=True)
    device_type = models.CharField(max_length=50, help_text="e.g., Mobile, Desktop, Tablet")
    os_name = models.CharField(max_length=50, help_text="e.g., Windows, iOS, Android")
    browser_name = models.CharField(max_length=50, help_text="e.g., Chrome, Safari")
    
    # Network & Location
    ip_address = models.GenericIPAddressField()
    isp_provider = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Activity
    is_trusted = models.BooleanField(default=False)
    last_used_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'device_id')

    def __str__(self):
        return f"{self.user.email} - {self.device_type} ({self.ip_address})"

# ============================================================================
# 6. IMMUTABLE AUDIT LOG
# ============================================================================
class SecurityAuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace_id = models.UUIDField(null=True, blank=True, db_index=True)
    
    actor = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50)
    description = models.TextField()
    
    # Linking the exact device used for this action
    device_used = models.ForeignKey(UserDeviceTracker, on_delete=models.SET_NULL, null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']