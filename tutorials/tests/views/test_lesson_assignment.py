
from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Lesson, Subject
from django.utils import timezone
from datetime import timedelta

class LessonAssignmentTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='@admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            type='admin',
            password='Password123'
        )
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
        self.lesson = Lesson.objects.create(
            student=self.student,
            subject='Python',
            date=timezone.now() + timedelta(days=1),
            duration=60,
            status='Pending'
        )
        self.client.login(username='@admin', password='Password123')

    def test_cannot_assign_student_as_tutor(self):
        other_student = User.objects.create_user(
            username='@student2',
            email='student2@example.com',
            first_name='Student2',
            last_name='User',
            type='student',
            password='Password123'
        )
        url = reverse('update_lesson', args=[self.lesson.id])
        response = self.client.post(url, {
            'tutor': other_student.id,
            'status': 'Approved',
            'student': self.student.id,
            'subject': 'Python',
            'date': self.lesson.date,
            'duration': 60
        })
        self.lesson.refresh_from_db()
        self.assertNotEqual(self.lesson.tutor, str(other_student.id))