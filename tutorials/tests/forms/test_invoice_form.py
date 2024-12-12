from django.test import TestCase
from tutorials.forms import InvoiceForm
from tutorials.models import User, Lesson, Invoice
from datetime import date, timedelta

class InvoiceFormTestCase(TestCase):
    """Unit tests for the InvoiceForm."""

    fixtures = ['tutorials/tests/fixtures/subjects.json', 'tutorials/tests/fixtures/users.json', 'tutorials/tests/fixtures/lessons.json']

    def setUp(self):
        """Set up test data."""
        self.student = User.objects.get(pk=1)
        self.other_student = User.objects.get(pk=4)
        self.tutor = User.objects.get(pk=2)
        self.lesson = Lesson.objects.get(pk=1)
        self.valid_data = {
            'student': self.student,
            'lesson': self.lesson,
            'amount': 100.00,
            'due_date': date.today() + timedelta(days=7),
            'paid': False,
        }

    def test_form_contains_required_fields(self):
        """Test that the form contains all required fields."""
        form = InvoiceForm()
        self.assertIn('student', form.fields)
        self.assertIn('lesson', form.fields)
        self.assertIn('amount', form.fields)
        self.assertIn('due_date', form.fields)
        self.assertIn('paid', form.fields)

    def test_form_accepts_valid_input(self):
        """Test that the form accepts valid input."""
        form = InvoiceForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_form_rejects_negative_amount(self):
        """Test that the form rejects a negative amount."""
        self.valid_data['amount'] = -10.00
        form = InvoiceForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)
        self.assertEqual(form.errors['amount'], ['Ensure this value is greater than or equal to 0.'])

    def test_form_accepts_null_lesson(self):
        """Test that the form accepts a null lesson."""
        self.valid_data['lesson'] = None
        form = InvoiceForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_form_rejects_missing_due_date(self):
        """Test that the form rejects missing due date."""
        self.valid_data.pop('due_date')
        form = InvoiceForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('due_date', form.errors)

    def test_form_rejects_missing_amount(self):
        """Test that the form rejects missing amount."""
        self.valid_data.pop('amount')
        form = InvoiceForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)

    def test_form_rejects_invalid_paid_choice(self):
        """Test that the form rejects an invalid paid choice."""
        self.valid_data['paid'] = 'invalid_choice'
        form = InvoiceForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('paid', form.errors)
