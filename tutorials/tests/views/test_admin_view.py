from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Lesson, Invoice
from django.utils import timezone
from datetime import timedelta

class AdminViewsTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='@adminuser',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            type='admin',
            password='Password123'
        )
        self.student = User.objects.create_user(
            username='@studentuser',
            email='student@example.com',
            first_name='Student',
            last_name='User',
            type='student',
            password='Password123'
        )
        self.client.login(username='@adminuser', password='Password123')

    def test_admin_dashboard_access(self):
        url = reverse('admin_dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/admin_dashboard.html')

    def test_admin_list_users(self):
        url = reverse('list_users')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/list_users.html')
        self.assertIn(self.student, response.context['users'])

    def test_admin_list_lessons(self):
        url = reverse('list_lessons')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/list_lessons.html')

    def test_admin_list_invoices(self):
        url = reverse('list_invoices')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/list_invoices.html')

    def test_non_admin_cannot_access_admin_dashboard(self):
        self.client.login(username='@studentuser', password='Password123')
        url = reverse('admin_dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)