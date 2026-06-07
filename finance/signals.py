from decimal import Decimal
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from django.db.models import Sum
from .models import InvoiceItem, Invoice

@receiver(post_save, sender=InvoiceItem)
def invoiceitem_post_save(sender, instance, **kwargs):
    """Recalculate invoice aggregates when an InvoiceItem is created or updated."""
    _recalculate_invoice_totals(instance.invoice_id)

@receiver(post_delete, sender=InvoiceItem)
def invoiceitem_post_delete(sender, instance, **kwargs):
    """Recalculate invoice aggregates when an InvoiceItem is deleted."""
    _recalculate_invoice_totals(instance.invoice_id)


def _recalculate_invoice_totals(invoice_id):
    if not invoice_id:
        return

    with transaction.atomic():
        # Lock the invoice row to prevent concurrent updates
        invoice_qs = Invoice.objects.select_for_update().filter(pk=invoice_id)
        invoice = invoice_qs.first()
        if not invoice:
            return

        # Aggregate subtotal from items
        agg = InvoiceItem.objects.filter(invoice=invoice).aggregate(total_sum=Sum('total'))
        sub_total = agg.get('total_sum') or Decimal('0.00')

        # Calculate tax amount (tax_percentage stored on Invoice)
        try:
            tax_percentage = Decimal(invoice.tax_percentage or 0)
        except Exception:
            tax_percentage = Decimal('0.00')

        tax_amount = (sub_total * tax_percentage / Decimal('100.00')).quantize(Decimal('0.01'))

        # Apply discount amount if any (assumed stored on invoice)
        discount = invoice.discount_amount or Decimal('0.00')

        grand_total = (sub_total + tax_amount - discount).quantize(Decimal('0.01'))

        # Use update() to avoid triggering model save signals again
        invoice_qs.update(sub_total=sub_total, tax_amount=tax_amount, grand_total=grand_total)
