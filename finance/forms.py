from django import forms
from .models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        # Workspace আমরা ভিউ থেকে অটোমেটিক দেব, তাই ফর্মে সেটি রাখব না
        fields = ['name', 'email', 'phone', 'company_name', 'tax_number', 'billing_address']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., John Doe'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'john@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+880 1XXX...极'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Tech Solutions Ltd.'}),
            'tax_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VAT / BIN Number'}),
            'billing_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full Billing Address...'}),
        }