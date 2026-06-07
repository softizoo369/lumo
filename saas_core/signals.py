from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone
from django.db import transaction # ডাটাবেস ট্রানজেকশন ইম্পোর্ট করা হলো
from datetime import timedelta

# অন্যান্য অ্যাপের মডেল
from accounts.models import UserProfile
from .models import Workspace, WorkspaceSubscription, SubscriptionPlan, WorkspaceSettings

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def auto_onboard_new_user(sender, instance, created, **kwargs):
    """
    User registration করলেই তার Profile, Workspace এবং Trial অটোমেটিক চালু হয়ে যাবে।
    Transaction Block ব্যবহার করা হয়েছে যাতে কোনো ডাটা মিসম্যাচ না হয়।
    """
    if created:
        # with transaction.atomic() নিশ্চিত করবে যে সব ডাটা একসাথে সেভ হবে, নতুবা কিছুই হবে না।
        with transaction.atomic():
            
            # 1. Create their Master Profile
            UserProfile.objects.create(user=instance)
            
            # Super admin হলে workspace বানানোর দরকার নাই
            if not instance.is_superuser:
                
                # 2. Find the Free/Starter Plan
                trial_plan = SubscriptionPlan.objects.first() 
                
                if trial_plan:
                    # 3. Auto-generate Workspace based on email
                    base_name = instance.email.split('@')[0].lower()
                    company_name = f"{base_name.capitalize()}'s Workspace"
                    subdomain = base_name.replace(".", "-") # Make it URL safe
                    
                    # Check uniqueness of subdomain
                    if Workspace.objects.filter(subdomain=subdomain).exists():
                        subdomain = f"{subdomain}-{instance.id.hex[:4]}"
                    
                    workspace = Workspace.objects.create(
                        owner=instance,
                        company_name=company_name,
                        subdomain=subdomain
                    )
                    
                    # 🚀 THE FIX: Avoid calling .save() inside post_save! Use .update() instead.
                    # এটি সরাসরি ডাটাবেস আপডেট করবে কিন্তু আবার সিগন্যাল ট্রিগার করবে না।
                    sender.objects.filter(pk=instance.pk).update(workspace_id=workspace.id)
                    
                    # 4. Give them 14 Days Free Trial
                    WorkspaceSubscription.objects.create(
                        workspace=workspace,
                        plan=trial_plan,
                        status='TRIAL',
                        current_period_end=timezone.now() + timedelta(days=14)
                    )                
                    
                    # 5. Auto-generate Settings Profile
                    WorkspaceSettings.objects.create(
                        workspace=workspace,
                    )