from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Lesson, Invoice, Notification, Subject
from datetime import datetime, timedelta
from django.utils import timezone

class StudentViewTestCase(TestCase):
    """Tests for the student views."""

    fixtures = ['tutorials/tests/fixtures/subjects.json', 'tutorials/tests/fixtures/users.json', 'tutorials/tests/fixtures/lessons.json', 'tutorials/tests/fixtures/invoices.json', 'tutorials/tests/fixtures/notifications.json']

    def setUp(self):
        """Set up test data and authenticate the student user."""
        self.student_user = User.objects.get(pk=1)
        self.client.login(username=self.student_user.username, password='Password123')

    def test_dashboard_view(self):
        """Test the student dashboard view."""
        response = self.client.get(reverse('student_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/dashboard.html')
        self.assertIn('user', response.context)
        self.assertIn('upcoming_lessons', response.context)
        self.assertIn('unread_notifications', response.context)

    def test_lessons_view(self):
        """Test the student lessons view."""
        response = self.client.get(reverse('student_lessons'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/list_lessons.html')
        self.assertIn('lessons', response.context)

    def test_schedule_view(self):
        """Test the student schedule view."""
        today = timezone.now()
        response = self.client.get(reverse('student_schedule', args=[today.year, today.month]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/view_schedule.html')
        self.assertIn('calendar', response.context)
        self.assertIn('month', response.context)
        self.assertIn('year', response.context)

    def test_requests_view(self):
        """Test the student lesson requests view."""
        response = self.client.get(reverse('student_requests'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/list_requests.html')
        self.assertIn('lessons', response.context)

    def test_create_request_view(self):
        """Test the create lesson request view."""
        response = self.client.get(reverse('create_request'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/create_update_request.html')
        self.assertIn('form', response.context)

        # Test creating a lesson request
        subject = Subject.objects.first()
        data = {
            'subject': subject.id,
            'date': timezone.now().replace(hour=10, minute=0) + timedelta(days=1),
            'duration': 60,
            'recurrence': 'None',
            'recurrence_end_date': '',
        }
        response = self.client.post(reverse('create_request'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation

    def test_update_request_view(self):
        """Test the update lesson request view."""
        lesson = Lesson.objects.filter(student=self.student_user).first()
        response = self.client.get(reverse('update_request', args=[lesson.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/create_update_request.html')
        self.assertIn('form', response.context)

        # Test updating the lesson request
        data = {
            'subject': lesson.subject.id,
            'date': timezone.now().replace(hour=10, minute=0) + timedelta(days=2),
            'duration': 90,
            'recurrence': 'Weekly',
            'recurrence_end_date': (timezone.now() + timedelta(days=30)).date(),
        }
        response = self.client.post(reverse('update_request', args=[lesson.id]), data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful update

    def test_delete_request_view(self):
        """Test the delete lesson request view."""
        lesson = Lesson.objects.filter(student=self.student_user).first()
        response = self.client.get(reverse('delete_request', args=[lesson.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/delete_request.html')
        self.assertIn('lesson', response.context)

        # Test deleting the lesson request
        response = self.client.post(reverse('delete_request', args=[lesson.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after successful deletion
        self.assertFalse(Lesson.objects.filter(id=lesson.id).exists())

    def test_invoices_view(self):
        """Test the student invoices view."""
        response = self.client.get(reverse('student_invoices'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/list_invoices.html')
        self.assertIn('invoices', response.context)
