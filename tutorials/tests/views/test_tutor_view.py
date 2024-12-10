from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Lesson, Subject
from django.utils import timezone
from datetime import timedelta

class TutorViewsTest(TestCase):
    """Tests the tutor views."""

    fixtures = ['tutorials/tests/fixtures/subjects.json', 'tutorials/tests/fixtures/users.json']

    def setUp(self):
        self.tutor = User.objects.get(pk=2)
        self.client.login(username=self.tutor.username, password='Password123')

    def test_tutor_dashboard_access(self):
        url = reverse('tutor_dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor/tutor_dashboard.html')

    def test_tutor_schedule_view(self):
        url = reverse('tutor_schedule')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor/tutor_schedule.html')

    def test_tutor_lessons_view(self):
        url = reverse('tutor_lessons')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor/tutor_lessons.html')

    def test_non_tutor_cannot_access_tutor_dashboard(self):
        student = User.objects.get(pk=1)
        self.client.login(username=student.username, password='Password123')
        url = reverse('tutor_dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_tutor_can_view_assigned_lessons(self):
        url = reverse('tutor_lessons')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)