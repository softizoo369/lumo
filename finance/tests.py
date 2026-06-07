from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from saas_core.models import Workspace
from .models import Client, Invoice, InvoiceItem


class InvoiceAggregateSignalsTest(TestCase):
	def setUp(self):
		User = get_user_model()
		self.user = User.objects.create_user(email='owner@example.com', password='pass')
		self.workspace = Workspace.objects.create(owner=self.user, company_name='Acme Ltd', subdomain='acme')

		self.client = Client.objects.create(workspace=self.workspace, name='John Doe')

		self.invoice = Invoice.objects.create(
			workspace=self.workspace,
			client=self.client,
			invoice_number='INV-001',
			date_issued=timezone.now().date(),
			due_date=timezone.now().date(),
			tax_percentage=Decimal('10.00'),
			discount_amount=Decimal('0.00')
		)

	def test_aggregate_on_item_create(self):
		item1 = InvoiceItem.objects.create(invoice=self.invoice, description='Service A', quantity=2, unit_price=Decimal('100.00'))
		# Allow signal to run and refresh
		self.invoice.refresh_from_db()
		self.assertEqual(self.invoice.sub_total, Decimal('200.00'))
		self.assertEqual(self.invoice.tax_amount, Decimal('20.00'))
		self.assertEqual(self.invoice.grand_total, Decimal('220.00'))

	def test_aggregate_on_item_update(self):
		item = InvoiceItem.objects.create(invoice=self.invoice, description='Service A', quantity=1, unit_price=Decimal('50.00'))
		self.invoice.refresh_from_db()
		self.assertEqual(self.invoice.sub_total, Decimal('50.00'))

		# Update item
		item.quantity = 3
		item.save()
		self.invoice.refresh_from_db()
		self.assertEqual(self.invoice.sub_total, Decimal('150.00'))
		self.assertEqual(self.invoice.tax_amount, Decimal('15.00'))

	def test_aggregate_on_item_delete(self):
		item1 = InvoiceItem.objects.create(invoice=self.invoice, description='Service A', quantity=1, unit_price=Decimal('30.00'))
		item2 = InvoiceItem.objects.create(invoice=self.invoice, description='Service B', quantity=2, unit_price=Decimal('20.00'))
		self.invoice.refresh_from_db()
		self.assertEqual(self.invoice.sub_total, Decimal('70.00'))

		# Delete one item
		item2.delete()
		self.invoice.refresh_from_db()
		self.assertEqual(self.invoice.sub_total, Decimal('30.00'))
