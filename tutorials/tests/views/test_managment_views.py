from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Lesson, Invoice
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone

User = get_user_model()

class LessonManagementTests(TestCase):
    def setUp(self):
        # Set up a test client and user
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

        # Set up a lesson instance
        self.lesson = Lesson.objects.create(
            student=self.user,
            subject='Python',
            date=timezone.now() + timedelta(days=1),
            duration=60,
            tutor='John Doe'
        )

    def test_view_upcoming_lessons(self):
        response = self.client.get(reverse('view_upcoming_lessons'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'view_upcoming_lessons.html')
        self.assertContains(response, 'All My Upcoming Lessons')
        self.assertContains(response, self.lesson.subject)

    def test_request_lesson_get(self):
        response = self.client.get(reverse('request_lesson'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'request_lesson.html')

    def test_request_lesson_post_valid(self):
        response = self.client.post(reverse('request_lesson'), {
            'subject': 'Java',
            'date': (timezone.now() + timedelta(days=2)).strftime('%Y-%m-%dT%H:%M'),
            'duration': 60
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        self.assertTrue(Lesson.objects.filter(subject='Java', student=self.user).exists())
        self.assertTrue(Invoice.objects.filter(student=self.user).exists())


    def test_update_lesson_get(self):
        response = self.client.get(reverse('update_lesson', args=[self.lesson.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update_lesson.html')
        self.assertContains(response, 'Update Lesson')

    def test_update_lesson_post_valid(self):
        response = self.client.post(reverse('update_lesson', args=[self.lesson.pk]), {
            'subject': 'Scala',
            'date': (timezone.now() + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M'),
            'duration': 90
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful update
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.subject, 'Scala')
        self.assertEqual(self.lesson.duration, 90)

    def test_remove_lesson_get(self):
        response = self.client.get(reverse('remove_lesson', args=[self.lesson.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'confirm_delete_lesson.html')
        self.assertContains(response, 'Confirm Delete Lesson')

    def test_remove_lesson_post(self):
        response = self.client.post(reverse('remove_lesson', args=[self.lesson.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect after successful deletion
        self.assertFalse(Lesson.objects.filter(pk=self.lesson.pk).exists())
