from django.test import TestCase
from django.utils import timezone
from tutorials.forms import LessonRequestForm
from datetime import datetime, timedelta

class LessonTimeValidationTest(TestCase):
    """Tests for lesson time and duration validation."""

    def setUp(self):
        # Set time to noon tomorrow to avoid working hours issues
        tomorrow = timezone.now() + timedelta(days=1)
        self.valid_datetime = tomorrow.replace(hour=12, minute=0, second=0, microsecond=0)
        
        self.form_input = {
            'subject': 'Python',
            'preferred_date': self.valid_datetime,
            'duration': 60,
            'recurrence': 'None',
            'end_date': None
        }

    def test_duration_must_be_multiple_of_15(self):
        for duration in [30, 45, 60]:
            self.form_input['duration'] = duration
            form = LessonRequestForm(data=self.form_input)
            self.assertTrue(form.is_valid(), f"Duration {duration} validation failed")


    def test_duration_minimum_value(self):
        self.form_input['duration'] = 15 
        form = LessonRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('duration', form.errors)

    def test_duration_maximum_value(self):
        """Test that duration cannot exceed 240 minutes."""
        test_durations = [241, 250, 300]
        for duration in test_durations:
            self.form_input['duration'] = duration
            form = LessonRequestForm(data=self.form_input)
            self.assertFalse(form.is_valid())
            self.assertIn('duration', form.errors)

    def test_valid_duration_values(self):
        """Test all valid duration values."""
        valid_durations = [30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180, 195, 210, 225, 240]
        for duration in valid_durations:
            self.form_input['duration'] = duration
            form = LessonRequestForm(data=self.form_input)
            self.assertTrue(form.is_valid(), f"Duration {duration} should be valid")

    def test_lesson_must_be_in_future(self):
        """Test that lesson date must be in the future."""
        past_dates = [
            timezone.now() - timedelta(days=1),
            timezone.now() - timedelta(hours=1),
            timezone.now() - timedelta(minutes=30)
        ]
        for date in past_dates:
            self.form_input['preferred_date'] = date
            form = LessonRequestForm(data=self.form_input)
            self.assertFalse(form.is_valid())
            self.assertIn('preferred_date', form.errors)

    def test_valid_future_dates(self):
        future_dates = [
            self.tomorrow_noon,
            self.tomorrow_noon + timedelta(days=7),
            self.tomorrow_noon + timedelta(days=30)
        ]
        for date in future_dates:
            self.form_input['preferred_date'] = date
            form = LessonRequestForm(data=self.form_input)
            self.assertTrue(form.is_valid(), f"Date {date} should be valid")

    def test_working_hours_start_time(self):
        """Test that lessons cannot start before 8 AM."""
        tomorrow = (timezone.now() + timedelta(days=1)).date()
        early_hours = [5, 6, 7]
        for hour in early_hours:
            date = datetime.combine(tomorrow, datetime.min.time().replace(hour=hour))
            self.form_input['preferred_date'] = date
            form = LessonRequestForm(data=self.form_input)
            self.assertFalse(form.is_valid())
            self.assertIn('preferred_date', form.errors)

    def test_working_hours_end_time(self):
        """Test that lessons cannot end after 8 PM."""
        tomorrow = (timezone.now() + timedelta(days=1)).date()
        late_hours = [19, 20, 21]  # 7 PM, 8 PM, 9 PM starts
        for hour in late_hours:
            date = datetime.combine(tomorrow, datetime.min.time().replace(hour=hour))
            self.form_input['preferred_date'] = date
            self.form_input['duration'] = 120  # 2 hours
            form = LessonRequestForm(data=self.form_input)
            self.assertFalse(form.is_valid())
            self.assertIn('preferred_date', form.errors)

    def test_valid_working_hours(self):
        """Test that lessons during working hours are valid."""
        tomorrow = (timezone.now() + timedelta(days=1)).date()
        valid_hours = [8, 10, 12, 14, 16]
        for hour in valid_hours:
            date = datetime.combine(tomorrow, datetime.min.time().replace(hour=hour))
            self.form_input['preferred_date'] = date
            self.form_input['duration'] = 60
            form = LessonRequestForm(data=self.form_input)
            self.assertTrue(form.is_valid(), f"Hour {hour} should be valid")