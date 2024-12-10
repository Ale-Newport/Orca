from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Lesson, Invoice
from django.utils import timezone
from datetime import timedelta

class AdminViewsTest(TestCase):

    fixtures = ['tutorials/tests/fixtures/subjects.json', 'tutorials/tests/fixtures/users.json']
    
    def setUp(self):
        self.admin = User.objects.get(pk=3)
        adminusername = self.admin.username
        self.client.login(username=adminusername, password='Password123')
        self.student = User.objects.get(pk=1)
        self.studentusername = self.student.username

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
        self.client.login(username=self.studentusername, password='Password123')
        url = reverse('admin_dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)