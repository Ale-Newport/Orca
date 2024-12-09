from django.test import TestCase
from django.utils import timezone
from tutorials.forms import LessonRequestForm
from datetime import datetime, timedelta

class LessonRecurrenceValidationTest(TestCase):
    """Tests for lesson recurrence validation."""

    def setUp(self):
        self.tomorrow_noon = timezone.now().replace(hour=12, minute=0) + timedelta(days=1)
        self.form_input = {
            'subject': 'Python',
            'preferred_date': self.tomorrow_noon,
            'duration': 60,
            'recurrence': 'None',
            'end_date': None
        }


    def test_valid_recurrence_types(self):
        recurrence_types = ['None'] 
        for recurrence in recurrence_types:
            self.form_input['recurrence'] = recurrence
            form = LessonRequestForm(data=self.form_input)
            self.assertTrue(form.is_valid(), f"Recurrence type {recurrence} should be valid")


    def test_invalid_recurrence_type(self):
        """Test that invalid recurrence types are rejected."""
        invalid_types = ['Yearly', 'Bi-weekly', 'Every other day', '']
        for recurrence in invalid_types:
            self.form_input['recurrence'] = recurrence
            form = LessonRequestForm(data=self.form_input)
            self.assertFalse(form.is_valid())

    def test_end_date_required_with_recurrence(self):
        """Test that end date is required when recurrence is set."""
        recurrence_types = ['Daily', 'Weekly', 'Monthly']
        for recurrence in recurrence_types:
            self.form_input['recurrence'] = recurrence
            self.form_input['end_date'] = None
            form = LessonRequestForm(data=self.form_input)
            self.assertFalse(form.is_valid())
            self.assertIn('end_date', form.errors)

    def test_end_date_not_required_without_recurrence(self):
        self.form_input['recurrence'] = 'None'
        self.form_input['end_date'] = None
        form = LessonRequestForm(data=self.form_input)
        self.assertTrue(form.is_valid())


    def test_valid_end_dates(self):
        self.form_input['recurrence'] = 'Weekly'
        valid_end_dates = [
            self.tomorrow_noon.date() + timedelta(days=14),  # Two weeks later
            self.tomorrow_noon.date() + timedelta(days=21),  # Three weeks later
        ]
        for end_date in valid_end_dates:
            self.form_input['end_date'] = end_date
            form = LessonRequestForm(data=self.form_input)
            self.assertTrue(form.is_valid(), f"End date {end_date} should be valid")