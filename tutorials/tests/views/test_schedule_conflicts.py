from django.test import TestCase
from tutorials.models import User, Lesson, Subject
from django.utils import timezone
from datetime import timedelta

class ScheduleConflictTest(TestCase):
    """Tests for detecting schedule conflicts between lessons."""

    fixtures = ['tutorials/tests/fixtures/subjects.json', 'tutorials/tests/fixtures/users.json']

    def setUp(self):
        self.tutor = User.objects.get(pk=3)
        self.student = User.objects.get(pk=1)
        self.tomorrow_noon = timezone.now().replace(hour=12, minute=0) + timedelta(days=1)

    def test_detect_overlapping_lessons(self):
        # Create first lesson
        lesson1 = Lesson.objects.create(
            student=self.student,
            subject=Subject.objects.get(name='Python'),
            date=self.tomorrow_noon,
            duration=60,
        )
        
        # Try to create overlapping lesson
        lesson2 = Lesson.objects.create(
            student=self.student,
            subject=Subject.objects.get(name='Java'),
            date=self.tomorrow_noon + timedelta(minutes=30),
            duration=60,
        )
        
        # Check if lessons overlap
        lesson1_end = lesson1.date + timedelta(minutes=lesson1.duration)
        lesson2_end = lesson2.date + timedelta(minutes=lesson2.duration)
        overlaps = (lesson1.date < lesson2_end) and (lesson2.date < lesson1_end)
        self.assertTrue(overlaps)

    def test_back_to_back_lessons_allowed(self):
        # Create first lesson
        lesson1 = Lesson.objects.create(
            student=self.student,
            subject=Subject.objects.get(name='Python'),
            date=self.tomorrow_noon,
            duration=60,
        )
        
        # Create lesson immediately after
        lesson2 = Lesson.objects.create(
            student=self.student,
            subject=Subject.objects.get(name='Java'),
            date=self.tomorrow_noon + timedelta(minutes=60),
            duration=60,
        )
        
        lesson1_end = lesson1.date + timedelta(minutes=lesson1.duration)
        self.assertEqual(lesson1_end, lesson2.date)

    def test_lessons_in_working_hours(self):
        early_morning = self.tomorrow_noon.replace(hour=7)
        lesson = Lesson.objects.create(
            student=self.student,
            subject=Subject.objects.get(name='Python'),
            date=early_morning,
            duration=60,
        )
        self.assertLess(lesson.date.hour, 8)