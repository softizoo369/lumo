from django import forms
from django.forms import inlineformset_factory
from .models import Client, Invoice, InvoiceItem

# ============================================================================
# 1. CLIENT FORM
# ============================================================================
class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'email', 'phone', 'company_name', 'tax_number', 'billing_address']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., John Doe'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'john@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+880 1XXX...'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Lumo Tech.'}),
            'tax_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VAT / BIN Number'}),
            'billing_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full Billing Address...'}),
        }


# ============================================================================
# 2. INVOICE FORMS (Main Invoice & Line Items)
# ============================================================================
class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['client', 'invoice_number', 'date_issued', 'due_date', 'status', 'tax_percentage', 'discount_amount', 'notes', 'terms_conditions']
        
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}),
            'invoice_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'INV-1001'}),
            'date_issued': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'tax_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'discount_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Thank you for your business.'}),
            'terms_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Payment due within 30 days.'}),
        }

    def __init__(self, *args, **kwargs):
        workspace = kwargs.pop('workspace', None)
        super(InvoiceForm, self).__init__(*args, **kwargs)
        if workspace:
            # Data Isolation: ড্রপডাউনে শুধু এই ওয়ার্কস্পেসের ক্লায়েন্টরা আসবে
            self.fields['client'].queryset = Client.objects.filter(workspace=workspace)


class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['description', 'quantity', 'unit_price']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control item-desc', 'placeholder': 'Service / Product Name'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control item-qty text-center', 'step': '1', 'min': '1'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control item-price text-end', 'step': '0.01', 'min': '0'}),
        }

# ============================================================================
# 3. FORMSETS (To handle multiple items in one invoice)
# ============================================================================
InvoiceItemFormSet = inlineformset_factory(
    Invoice, InvoiceItem, form=InvoiceItemForm,
    extra=1, can_delete=True
)