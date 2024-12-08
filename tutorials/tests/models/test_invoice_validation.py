from django.test import TestCase
from django.utils import timezone
from tutorials.models import Invoice, User
from decimal import Decimal
from datetime import timedelta

class InvoiceValidationTest(TestCase):
    """Tests for Invoice model validation."""

    def setUp(self):
        self.student = User.objects.create(
            username='@student',
            email='student@example.com',
            first_name='Student',
            last_name='Test',
            type='student'
        )

    def test_valid_amount_values(self):
        """Test that valid amount values are accepted."""
        valid_amounts = [
            Decimal('0.50'),
            Decimal('1.00'),
            Decimal('50.00'),
            Decimal('100.50'),
            Decimal('999.99')
        ]
        for amount in valid_amounts:
            invoice = Invoice(
                student=self.student,
                amount=amount,
                due_date=timezone.now().date() + timedelta(days=30)
            )
            try:
                invoice.full_clean()
                self.assertTrue(True)
            except:
                self.fail(f"Amount {amount} should be valid")

    def test_invoice_issued_date_automatic(self):
        """Test that issued_date is automatically set."""
        invoice = Invoice.objects.create(
            student=self.student,
            amount=Decimal('50.00'),
            due_date=timezone.now().date() + timedelta(days=30)
        )
        self.assertIsNotNone(invoice.issued_date)
        self.assertTrue(isinstance(invoice.issued_date, type(timezone.now().date())))

    def test_invoice_default_payment_status(self):
        """Test that new invoices are unpaid by default."""
        invoice = Invoice.objects.create(
            student=self.student,
            amount=Decimal('50.00'),
            due_date=timezone.now().date() + timedelta(days=30)
        )
        self.assertFalse(invoice.paid)

    def test_invoice_string_representation(self):
        """Test invoice string representation."""
        invoice = Invoice.objects.create(
            student=self.student,
            amount=Decimal('50.00'),
            due_date=timezone.now().date() + timedelta(days=30)
        )
        self.assertIn(str(invoice.id), str(invoice))
        self.assertIn(self.student.username, str(invoice))