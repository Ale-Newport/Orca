from django.test import TestCase
from decimal import Decimal
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from tutorials.models import User, Lesson, Invoice

class InvoiceCreationTest(TestCase):
    """Tests the Invoice model."""

    fixtures = ['tutorials/tests/fixtures/subjects.json', 'tutorials/tests/fixtures/users.json', 'tutorials/tests/fixtures/lessons.json']

    def setUp(self):
        self.student = User.objects.get(pk=1)
        self.lesson = Lesson.objects.get(pk=1)
        self.due_date = timezone.now().date() + timedelta(days=30)
        self.amount = Decimal('50.00')

    def test_invoice_valid_creation(self):
        invoice = Invoice.objects.create(
            student=self.student,
            lesson=None,
            amount=self.amount,
            due_date=self.due_date,
            paid=False,
        )
        self.assertTrue(invoice)

    def test_invoice_has_student_field(self):
        invoice = Invoice.objects.create(
            student=self.student,
            lesson=None,
            amount=self.amount,
            due_date=self.due_date,
            paid=False,
        )
        self.assertEqual(invoice.student, self.student)

    def test_invoice_has_lesson_field(self):
        invoice = Invoice.objects.create(
            student=self.student,
            lesson=self.lesson,
            amount=self.amount,
            due_date=self.due_date,
            paid=False,
        )
        self.assertEqual(invoice.lesson, self.lesson)

    def test_invoice_has_amount_field(self):
        invoice = Invoice.objects.create(
            student=self.student,
            lesson=None,
            amount=self.amount,
            due_date=self.due_date,
            paid=False,
        )
        self.assertEqual(invoice.amount, self.amount)

    def test_invoice_has_due_date_field(self):
        invoice = Invoice.objects.create(
            student=self.student,
            lesson=None,
            amount=self.amount,
            due_date=self.due_date,
            paid=False,
        )
        self.assertEqual(invoice.due_date, self.due_date)

    def test_invoice_has_paid_field(self):
        invoice = Invoice.objects.create(
            student=self.student,
            lesson=None,
            amount=self.amount,
            due_date=self.due_date,
            paid=True,
        )
        self.assertTrue(invoice.paid)

    def test_invoice_default_unpaid(self):
        invoice = Invoice.objects.create(
            student=self.student,
            lesson=None,
            amount=self.amount,
            due_date=self.due_date,
            # paid field not set
        )
        self.assertFalse(invoice.paid)

    def test_invoice_overdue(self):
        invoice = Invoice.objects.create(
            student=self.student,
            lesson=None,
            amount=self.amount,
            due_date=timezone.now().date() - timedelta(days=1),
            paid=False,
        )
        self.assertTrue(invoice.is_overdue())

    def test_invoice_not_overdue(self):
        invoice = Invoice.objects.create(
            student=self.student,
            lesson=None,
            amount=self.amount,
            due_date=timezone.now().date() + timedelta(days=1),
            paid=False,
        )
        self.assertFalse(invoice.is_overdue())
    
    def test_invoice_string_representation(self):
        invoice = Invoice.objects.create(
            student=self.student,
            lesson=None,
            amount=self.amount,
            due_date=self.due_date,
            paid=False,
        )
        self.assertIn(str(invoice.id), str(invoice))
        self.assertIn(str(self.student), str(invoice))
        self.assertIn('Unpaid', str(invoice))

class InvoiceAmountTest(TestCase):
    """Tests the Invoice model amount field."""

    fixtures = ['tutorials/tests/fixtures/subjects.json', 'tutorials/tests/fixtures/users.json', 'tutorials/tests/fixtures/lessons.json']

    def setUp(self):
        self.student = User.objects.get(pk=1)
        self.due_date = timezone.now().date() + timedelta(days=30)

    def test_invoice_default_amount(self):
        invoice = Invoice.objects.create(
            student=self.student,
            lesson=None,
            # amount field not set
            due_date=self.due_date,
            paid=False,
        )
        self.assertEqual(invoice.amount, Decimal('0.00'))

    def test_invoice_amount_zero(self):
        invoice = Invoice.objects.create(
            student=self.student,
            lesson=None,
            amount=Decimal('0.00'),
            due_date=self.due_date,
            paid=False,
        )
        self.assertEqual(invoice.amount, Decimal('0.00'))

    def test_invoice_amount_valid(self):
        invoice = Invoice.objects.create(
            student=self.student,
            lesson=None,
            amount=Decimal('50.00'),
            due_date=self.due_date,
            paid=False,
        )
        self.assertEqual(invoice.amount, Decimal('50.00'))

class InvoiceStudentLessonTest(TestCase):
    """Tests the Invoice model student field."""

    fixtures = ['tutorials/tests/fixtures/subjects.json', 'tutorials/tests/fixtures/users.json', 'tutorials/tests/fixtures/lessons.json']

    def setUp(self):
        self.student = User.objects.get(pk=1)
        self.lesson_of_student = Lesson.objects.get(pk=1)
        self.lesson_of_other_student = Lesson.objects.get(pk=2)
        self.due_date = timezone.now().date() + timedelta(days=30)
        self.amount = Decimal('50.00')
    
    def test_invoice_student_lesson_no_match(self):
        with self.assertRaises(ValidationError):
            invoice = Invoice(
                student=self.student,
                lesson=self.lesson_of_other_student,
                amount=self.amount,
                due_date=self.due_date,
                paid=False,
            )
            invoice.clean()
    
    def test_invoice_student_lesson_match(self):
        invoice = Invoice.objects.create(
            student=self.student,
            lesson=self.lesson_of_student,
            amount=self.amount,
            due_date=self.due_date,
            paid=False,
        )
        self.assertEqual(invoice.student, self.student)
        self.assertEqual(invoice.lesson, self.lesson_of_student)

    def test_invoice_default_lesson_none(self):
        invoice = Invoice.objects.create(
            student=self.student,
            # lesson field not set
            amount=self.amount,
            due_date=self.due_date,
            paid=False,
        )
        self.assertEqual(invoice.lesson, None)

