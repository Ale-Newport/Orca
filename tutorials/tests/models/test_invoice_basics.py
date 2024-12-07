from django.test import TestCase
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from tutorials.models import User, Lesson, Invoice

class InvoiceBasicsTest(TestCase):
    """Tests basic attributes and behaviors of the Invoice model."""

    def setUp(self):
        self.student = User.objects.create(
            username='@student',
            email='student@example.com',
            first_name='Student',
            last_name='Test',
            type='student'
        )

    def test_invoice_has_amount_field(self):
        invoice = Invoice.objects.create(
            student=self.student,
            amount=Decimal('50.00'),
            due_date=timezone.now().date() + timedelta(days=30)
        )
        self.assertEqual(invoice.amount, Decimal('50.00'))

    def test_invoice_has_issued_date(self):
        invoice = Invoice.objects.create(
            student=self.student,
            amount=Decimal('50.00'),
            due_date=timezone.now().date() + timedelta(days=30)
        )
        self.assertIsNotNone(invoice.issued_date)
        self.assertEqual(invoice.issued_date, timezone.now().date())

    def test_invoice_default_unpaid(self):
        invoice = Invoice.objects.create(
            student=self.student,
            amount=Decimal('50.00'),
            due_date=timezone.now().date() + timedelta(days=30)
        )
        self.assertFalse(invoice.paid)

    def test_invoice_belongs_to_student(self):
        invoice = Invoice.objects.create(
            student=self.student,
            amount=Decimal('50.00'),
            due_date=timezone.now().date() + timedelta(days=30)
        )
        self.assertEqual(invoice.student, self.student)

    def test_invoice_rejects_negative_amount(self):
        with self.assertRaises(ValueError):
            Invoice.objects.create(
                student=self.student,
                amount=Decimal('-50.00'),
                due_date=timezone.now().date() + timedelta(days=30)
            )

    def test_invoice_decimal_places(self):
        amount = Decimal('50.55')
        invoice = Invoice.objects.create(
            student=self.student,
            amount=amount,
            due_date=timezone.now().date() + timedelta(days=30)
        )
        self.assertEqual(invoice.amount, amount)


class InvoiceGenerationTest(TestCase):
    """Tests invoice creation logic related to lessons."""

    def setUp(self):
        self.student = User.objects.create_user(
            username='@student',
            email='student@example.com',
            first_name='Student',
            last_name='User',
            type='student',
            password='Password123'
        )
        self.lesson = Lesson.objects.create(
            student=self.student,
            subject='Python',
            date=timezone.now() + timedelta(days=1),
            duration=60,
            status='Approved'
        )

    def test_invoice_created_with_lesson(self):
        invoice = Invoice.objects.create(
            student=self.student,
            amount=Decimal('50.00'),
            due_date=timezone.now().date() + timedelta(days=30)
        )
        self.assertEqual(invoice.student, self.lesson.student)

    def test_invoice_amount_calculation(self):
        hourly_rate = Decimal('50.00')
        expected_amount = hourly_rate * Decimal(self.lesson.duration) / Decimal(60)
        invoice = Invoice.objects.create(
            student=self.student,
            amount=expected_amount,
            due_date=timezone.now().date() + timedelta(days=30)
        )
        self.assertEqual(invoice.amount, expected_amount)

    def test_invoice_due_date_after_lesson(self):
        invoice = Invoice.objects.create(
            student=self.student,
            amount=Decimal('50.00'),
            due_date=timezone.now().date() + timedelta(days=30)
        )
        self.assertGreater(invoice.due_date, self.lesson.date.date())

    def test_multiple_lessons_one_invoice(self):
        lesson2 = Lesson.objects.create(
            student=self.student,
            subject='Java',
            date=timezone.now() + timedelta(days=2),
            duration=90,
            status='Approved'
        )
        total_duration = self.lesson.duration + lesson2.duration
        hourly_rate = Decimal('50.00')
        expected_amount = hourly_rate * Decimal(total_duration) / Decimal(60)
        invoice = Invoice.objects.create(
            student=self.student,
            amount=expected_amount,
            due_date=timezone.now().date() + timedelta(days=30)
        )
        self.assertEqual(invoice.amount, expected_amount)

    def test_zero_duration_lesson_creates_no_invoice(self):
        zero_lesson = Lesson.objects.create(
            student=self.student,
            subject='Empty',
            date=timezone.now() + timedelta(days=1),
            duration=0,
            status='Approved'
        )
        invoice = Invoice.objects.filter(student=self.student, amount=0)
        self.assertFalse(invoice.exists())
