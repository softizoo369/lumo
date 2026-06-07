from django.db import models
from django.conf import settings
import uuid
from django.db.models import Index

# আপনার saas_core থেকে Workspace এবং GlobalCurrency ইম্পোর্ট করে নিন
from saas_core.models import Workspace, GlobalCurrency

# ============================================================================
# 1. CLIENT / CUSTOMER DIRECTORY
# ============================================================================
class Client(models.Model):
    """
    যাদেরকে ইনভয়েস পাঠানো হবে (Workspace এর কাস্টমার)।
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='clients')
    
    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    company_name = models.CharField(max_length=150, blank=True, null=True)
    
    billing_address = models.TextField(blank=True)
    tax_number = models.CharField(max_length=50, blank=True, help_text="VAT/BIN number of the client")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('workspace', 'email') # একই ইমেইলের ডুপ্লিকেট ক্লায়েন্ট রোধ করতে
        indexes = [
            Index(fields=['workspace', 'email']),
        ]

    def __str__(self):
        return self.name


# ============================================================================
# 2. INVOICE ENGINE
# ============================================================================
class Invoice(models.Model):
    """
    মূল ইনভয়েস টেবিল। 
    """
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('UNPAID', 'Unpaid / Pending'),
        ('PARTIAL', 'Partially Paid'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
        ('CANCELLED', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='invoices')
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='invoices')
    
    invoice_number = models.CharField(max_length=50, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    # Dates
    date_issued = models.DateField()
    due_date = models.DateField()
    
    # Financials
    sub_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Localization: Specific currency for this invoice (Overrides workspace default if needed)
    currency = models.ForeignKey(GlobalCurrency, on_delete=models.SET_NULL, null=True, blank=True)
    
    notes = models.TextField(blank=True, help_text="e.g., Thank you for your business.")
    terms_conditions = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('workspace', 'invoice_number') # এক ওয়ার্কস্পেসে একই ইনভয়েস নাম্বার ২ বার হবে না
        indexes = [
            Index(fields=['workspace', 'status']),
            Index(fields=['workspace', 'date_issued']),
        ]

    def __str__(self):
        return f"{self.invoice_number} - {self.client.name}"


# ============================================================================
# 3. INVOICE LINE ITEMS
# ============================================================================
class InvoiceItem(models.Model):
    """
    ইনভয়েসের ভেতরের প্রোডাক্ট বা সার্ভিসের লিস্ট।
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        # অটোমেটিক টোটাল ক্যালকুলেট করার লজিক
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            Index(fields=['invoice']),
        ]

    def __str__(self):
        return f"{self.description} (x{self.quantity})"