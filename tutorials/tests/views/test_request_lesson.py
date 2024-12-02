from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from tutorials.models import User, Lesson
from datetime import timedelta

class LessonRequestTestCase(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username='@student',
            password='Password123',
            email='student@example.com',
            type='student'
        )
        self.url = reverse('request_lesson')
        self.client.login(username='@student', password='Password123')

    def test_get_request_lesson_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'request_lesson.html')

    def test_post_valid_lesson_request(self):
        data = {
            'subject': 'Python',
            'preferred_date': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'),
            'duration': 60,
            'recurrence': 'None',
            'notes': 'Focus on Django.'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Lesson.objects.filter(student=self.student, subject='Python').exists())

    def test_post_invalid_lesson_request(self):
        data = {
            'subject': '',
            'preferred_date': '',
            'duration': '',
            'recurrence': 'None',
            'notes': ''
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'subject', 'This field is required.')
        self.assertFormError(response, 'form', 'preferred_date', 'This field is required.')
        self.assertFormError(response, 'form', 'duration', 'This field is required.')
