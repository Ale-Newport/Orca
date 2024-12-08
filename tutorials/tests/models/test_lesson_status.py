from django.test import TestCase
from tutorials.models import User, Lesson
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse

class LessonStatusTest(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username='@student2',
            email='student2@example.com',
            first_name='Student',
            last_name='Two',
            type='student',
            password='Password123'
        )
        self.future_date = timezone.now() + timedelta(days=1)

    def test_lesson_initial_status_pending(self):
        lesson = Lesson.objects.create(
            student=self.student,
            subject='Python',
            date=self.future_date,
            duration=60
        )
        self.assertEqual(lesson.status, 'Pending')

    def test_lesson_status_change(self):
        lesson = Lesson.objects.create(
            student=self.student,
            subject='Python',
            date=self.future_date,
            duration=60
        )
        lesson.status = 'Approved'
        lesson.save()
        self.assertEqual(lesson.status, 'Approved')

    def test_lesson_duration_validation(self):
        lesson = Lesson.objects.create(
            student=self.student,
            subject='Python',
            date=self.future_date,
            duration=60
        )
        self.assertTrue(30 <= lesson.duration <= 240)

    def test_lesson_string_representation(self):
        lesson = Lesson.objects.create(
            student=self.student,
            subject='Python',
            date=self.future_date,
            duration=60
        )
        self.assertIn('Python', str(lesson))
        self.assertIn(self.student.username, str(lesson))

    def test_lesson_default_tutor_value(self):
        lesson = Lesson.objects.create(
            student=self.student,
            subject='Python',
            date=self.future_date,
            duration=60
        )
        self.assertEqual(lesson.tutor, "Unknown Tutor")
    
class StudentLessonModificationTest(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username='@student',
            email='student@example.com',
            first_name='Student',
            last_name='Test',
            type='student',
            password='Password123'
        )
        self.tomorrow = timezone.now() + timedelta(days=1)
        self.lesson = Lesson.objects.create(
            student=self.student,
            subject='Python',
            date=self.tomorrow.replace(hour=12, minute=0),
            duration=60,
            status='Pending'
        )
        self.client.login(username='@student', password='Password123')


    def test_student_cannot_modify_other_student_lesson(self):
        other_student = User.objects.create_user(
            username='@otherstudent',
            email='other@example.com',
            first_name='Other',
            last_name='Student',
            type='student',
            password='Password123'
        )
        other_lesson = Lesson.objects.create(
            student=other_student,
            subject='Python',
            date=timezone.now() + timedelta(days=1),
            duration=60
        )
        url = reverse('update_request', args=[other_lesson.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)