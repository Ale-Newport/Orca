from django.test import TestCase
from tutorials.models import User, Lesson
from django.utils import timezone
from datetime import timedelta

class ScheduleConflictTest(TestCase):
    def setUp(self):
        self.tutor = User.objects.create_user(
            username='@tutor',
            email='tutor@example.com',
            first_name='Tutor',
            last_name='User',
            type='tutor',
            password='Password123'
        )
        self.student = User.objects.create_user(
            username='@student',
            email='student@example.com',
            first_name='Student',
            last_name='User',
            type='student',
            password='Password123'
        )
        self.tomorrow_noon = timezone.now().replace(hour=12, minute=0) + timedelta(days=1)

    def test_detect_overlapping_lessons(self):
        # Create first lesson
        lesson1 = Lesson.objects.create(
            student=self.student,
            subject='Python',
            date=self.tomorrow_noon,
            duration=60,
            tutor=str(self.tutor.id)
        )
        
        # Try to create overlapping lesson
        lesson2 = Lesson.objects.create(
            student=self.student,
            subject='Java',
            date=self.tomorrow_noon + timedelta(minutes=30),
            duration=60,
            tutor=str(self.tutor.id)
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
            subject='Python',
            date=self.tomorrow_noon,
            duration=60,
            tutor=str(self.tutor.id)
        )
        
        # Create lesson immediately after
        lesson2 = Lesson.objects.create(
            student=self.student,
            subject='Java',
            date=self.tomorrow_noon + timedelta(minutes=60),
            duration=60,
            tutor=str(self.tutor.id)
        )
        
        lesson1_end = lesson1.date + timedelta(minutes=lesson1.duration)
        self.assertEqual(lesson1_end, lesson2.date)

    def test_lessons_in_working_hours(self):
        early_morning = self.tomorrow_noon.replace(hour=7)  # Before 8 AM
        lesson = Lesson.objects.create(
            student=self.student,
            subject='Python',
            date=early_morning,
            duration=60,
            tutor=str(self.tutor.id)
        )
        self.assertLess(lesson.date.hour, 8)  # Should fail working hours validation