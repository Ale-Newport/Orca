from django import forms
from django.test import TestCase
from tutorials.forms import RequestForm
from tutorials.models import Subject
from datetime import timedelta
from django.utils import timezone

class RequestFormTestCase(TestCase):
    """Unit tests for the RequestForm."""

    fixtures = ['tutorials/tests/fixtures/subjects.json']

    def setUp(self):
        self.subject = Subject.objects.get(pk=1)
        self.valid_date = timezone.now().replace(hour=10, minute=0) + timedelta(days=1)
        self.form_input = {
            'subject': self.subject,
            'date': self.valid_date,
            'duration': 60,
            'recurrence': 'None',
            'recurrence_end_date': None,
        }

    def test_form_contains_required_fields(self):
        form = RequestForm()
        self.assertIn('subject', form.fields)
        self.assertIn('date', form.fields)
        self.assertIn('duration', form.fields)
        self.assertIn('recurrence', form.fields)
        self.assertIn('recurrence_end_date', form.fields)

    def test_form_accepts_valid_input(self):
        form = RequestForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_past_date(self):
        self.form_input['date'] = timezone.now() - timedelta(days=1)
        form = RequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('date', form.errors)

    def test_form_rejects_invalid_duration_not_multiple_of_15(self):
        self.form_input['duration'] = 50  # Not a multiple of 15
        form = RequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('duration', form.errors)

    def test_form_rejects_duration_below_minimum(self):
        self.form_input['duration'] = 25  # Below the minimum of 30
        form = RequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('duration', form.errors)

    def test_form_rejects_duration_above_maximum(self):
        self.form_input['duration'] = 300  # Above the maximum of 240
        form = RequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('duration', form.errors)

    def test_form_rejects_invalid_recurrence_without_end_date(self):
        self.form_input['recurrence'] = 'Weekly'
        self.form_input['recurrence_end_date'] = None
        form = RequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('recurrence_end_date', form.errors)

    def test_form_rejects_invalid_recurrence_end_date_without_recurrence(self):
        self.form_input['recurrence'] = 'None'
        self.form_input['recurrence_end_date'] = timezone.now().date() + timedelta(days=10)
        form = RequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('recurrence', form.errors)

    def test_form_rejects_recurrence_end_date_before_date(self):
        self.form_input['recurrence'] = 'Weekly'
        self.form_input['recurrence_end_date'] = self.valid_date.date() - timedelta(days=1)
        form = RequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('recurrence_end_date', form.errors)

    def test_form_rejects_date_outside_working_hours(self):
        self.form_input['date'] = timezone.now().replace(hour=7, minute=0) + timedelta(days=1)  # Before 8:00 AM
        form = RequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('date', form.errors)

        self.form_input['date'] = timezone.now().replace(hour=21, minute=0) + timedelta(days=1)  # After 8:00 PM
        form = RequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('date', form.errors)

    def test_form_rejects_end_time_outside_working_hours(self):
        self.form_input['date'] = timezone.now().replace(hour=19, minute=30) + timedelta(days=1)
        self.form_input['duration'] = 90  # End time goes beyond 8:00 PM
        form = RequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('date', form.errors)
