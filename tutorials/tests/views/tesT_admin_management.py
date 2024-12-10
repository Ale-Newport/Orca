from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Lesson, Invoice
from django.utils import timezone
from datetime import timedelta

class AdminManagementTest(TestCase):
    """Tests the Invoice model."""
    
    fixtures = ['tutorials/tests/fixtures/subjects.json', 'tutorials/tests/fixtures/users.json']

    
    def setUp(self):
        self.admin = User.objects.get(pk=3)
        username = self.admin.username
        self.client.login(username=username, password='Password123')

    def test_admin_can_create_user(self):
        url = reverse('create_user')
        user_data = {
            'username': '@newuser',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'type': 'student',
        }
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_admin_can_view_notifications(self):
        url = reverse('list_notifications')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/list_notifications.html')

    def test_admin_dashboard_shows_counts(self):
        url = reverse('admin_dashboard')
        response = self.client.get(url)
        self.assertIn('total_users', response.context)
        self.assertIn('total_lessons', response.context)
        self.assertIn('total_invoices', response.context)

    def test_admin_can_filter_users(self):
        url = reverse('list_users')
        response = self.client.get(url, {'type': 'student'})
        self.assertEqual(response.status_code, 200)

    def test_admin_can_filter_lessons(self):
        url = reverse('list_lessons')
        response = self.client.get(url, {'status': 'Pending'})
        self.assertEqual(response.status_code, 200)