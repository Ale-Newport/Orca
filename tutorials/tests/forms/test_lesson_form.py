from django import forms
from django.test import TestCase
from tutorials.forms import LessonForm
from tutorials.models import User, Lesson, Subject
from datetime import timedelta
from django.utils import timezone

class LessonFormTestCase(TestCase):
    """Unit tests of the lesson form."""

    fixtures = ['tutorials/tests/fixtures/subjects.json', 'tutorials/tests/fixtures/users.json']

    def setUp(self):
        self.student = User.objects.get(username='@charlie')
        self.tutor = User.objects.get(username='@janedoe')
        self.subject = Subject.objects.get(name='Python')
        self.form_input = {
            'student': self.student,
            'tutor': self.tutor,
            'subject': self.subject,
            'date': (timezone.now() + timedelta(days=1)),
            'duration': 60,
            'status': 'Approved',
            'recurrence': 'None',
            'recurrence_end_date': None
        }

    def test_form_contains_required_fields(self):
        form = LessonForm()
        self.assertIn('student', form.fields)
        self.assertIn('tutor', form.fields)
        self.assertIn('subject', form.fields)
        self.assertIn('date', form.fields)
        self.assertIn('duration', form.fields)
        self.assertIn('status', form.fields)
        self.assertIn('recurrence', form.fields)
        self.assertIn('recurrence_end_date', form.fields)

    def test_form_accepts_valid_input(self):
        form = LessonForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_past_date(self):
        self.form_input['date'] = (timezone.now() - timedelta(days=1))
        form = LessonForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('date', form.errors)

    def test_form_rejects_invalid_duration(self):
        self.form_input['duration'] = 25
        form = LessonForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('duration', form.errors)

    def test_form_rejects_invalid_recurrence(self):
        self.form_input['recurrence'] = 'Weekly'
        self.form_input['recurrence_end_date'] = None
        form = LessonForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('recurrence_end_date', form.errors)

    def test_form_rejects_invalid_student_type(self):
        form_input = {
            'student': self.tutor,
            'tutor': self.tutor,
            'subject': self.subject,
            'date': (timezone.now() + timedelta(days=1)),
            'duration': 60,
            'status': 'Approved',
            'recurrence': 'None',
            'recurrence_end_date': None
        }
        form = LessonForm(data=form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('student', form.errors)

    def test_form_rejects_invalid_tutor_type(self):
        form_input = {
            'student': self.student,
            'tutor': self.student,
            'subject': self.subject,
            'date': (timezone.now() + timedelta(days=1)),
            'duration': 60,
            'status': 'Approved',
            'recurrence': 'None',
            'recurrence_end_date': None
        }
        form = LessonForm(data=form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('tutor', form.errors)

    def test_form_rejects_overlapping_lessons(self):
        Lesson.objects.create(
            student=self.student,
            tutor=self.tutor,
            subject=self.subject,
            date=timezone.now() + timedelta(days=1),
            duration=60,
            status='Approved',
        )
        form = LessonForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('date', form.errors)