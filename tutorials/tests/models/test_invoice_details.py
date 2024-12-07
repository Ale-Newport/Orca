from django.test import TestCase
from tutorials.models import User, Invoice
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

class InvoiceDetailTest(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username='@student1',
            email='student1@example.com',
            first_name='Student',
            last_name='One',
            type='student',
            password='Password123'
        )
        self.due_date = timezone.now().date() + timedelta(days=30)

    def test_invoice_initial_paid_status(self):
        invoice = Invoice.objects.create(
            student=self.student,
            amount=Decimal('50.00'),
            due_date=self.due_date
        )
        self.assertFalse(invoice.paid)

    def test_invoice_issued_date_auto_set(self):
        invoice = Invoice.objects.create(
            student=self.student,
            amount=Decimal('50.00'),
            due_date=self.due_date
        )
        self.assertIsNotNone(invoice.issued_date)

    def test_invoice_string_representation(self):
        invoice = Invoice.objects.create(
            student=self.student,
            amount=Decimal('50.00'),
            due_date=self.due_date
        )
        self.assertIn(str(invoice.id), str(invoice))
        self.assertIn(self.student.username, str(invoice))

    def test_invoice_amount_decimal_places(self):
        amount = Decimal('50.25')
        invoice = Invoice.objects.create(
            student=self.student,
            amount=amount,
            due_date=self.due_date
        )
        self.assertEqual(invoice.amount, amount)

    def test_invoice_student_relationship(self):
        invoice = Invoice.objects.create(
            student=self.student,
            amount=Decimal('50.00'),
            due_date=self.due_date
        )
        self.assertEqual(invoice.student.username, '@student1')