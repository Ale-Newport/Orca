from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Lesson, Invoice, Notification, Subject
from datetime import date, timedelta
from django.utils import timezone


class AdminViewFilterSearchTestCase(TestCase):
    """Extended tests for filtering, ordering, and searching in admin views."""

    fixtures = ['tutorials/tests/fixtures/subjects.json', 'tutorials/tests/fixtures/users.json', 'tutorials/tests/fixtures/lessons.json', 'tutorials/tests/fixtures/invoices.json', 'tutorials/tests/fixtures/notifications.json']

    def setUp(self):
        """Set up test data and authenticate the admin user."""
        self.admin_user = User.objects.get(pk=3)
        self.client.login(username=self.admin_user.username, password='Password123')

    def test_admin_dashboard_shows_counts(self):
        url = reverse('admin_dashboard')
        response = self.client.get(url)
        self.assertIn('total_users', response.context)
        self.assertIn('total_lessons', response.context)
        self.assertIn('total_invoices', response.context)

    # Filtering Tests
    def test_filter_users_by_type(self):
        """Test filtering users by type."""
        response = self.client.get(reverse('list_users') + '?type=student')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/list_users.html')
        users = response.context['users']
        self.assertTrue(all(user.type == 'student' for user in users))

    def test_filter_lessons_by_status(self):
        """Test filtering lessons by status."""
        response = self.client.get(reverse('list_lessons') + '?status=Approved')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/list_lessons.html')
        lessons = response.context['lessons']
        self.assertTrue(all(lesson.status == 'Approved' for lesson in lessons))

    def test_filter_invoices_by_paid_status(self):
        """Test filtering invoices by paid status."""
        response = self.client.get(reverse('list_invoices') + '?paid=True')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/list_invoices.html')
        invoices = response.context['invoices']
        self.assertTrue(all(invoice.paid is True for invoice in invoices))

    def test_filter_notifications_by_read_status(self):
        """Test filtering notifications by read status."""
        response = self.client.get(reverse('list_notifications') + '?is_read=False')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/list_notifications.html')
        notifications = response.context['notifications']
        self.assertTrue(all(notification.is_read is False for notification in notifications))

    # Ordering Tests
    def test_order_users_by_username(self):
        """Test ordering users by username."""
        response = self.client.get(reverse('list_users') + '?order_by=username')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/list_users.html')
        users = response.context['users']
        usernames = [user.username for user in users]
        self.assertEqual(usernames, sorted(usernames))

    def test_order_lessons_by_date(self):
        """Test ordering lessons by date."""
        response = self.client.get(reverse('list_lessons') + '?order_by=date')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/list_lessons.html')
        lessons = response.context['lessons']
        dates = [lesson.date for lesson in lessons]
        self.assertEqual(dates, sorted(dates))

    def test_order_invoices_by_amount(self):
        """Test ordering invoices by amount."""
        response = self.client.get(reverse('list_invoices') + '?order_by=amount')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/list_invoices.html')
        invoices = response.context['invoices']
        amounts = [invoice.amount for invoice in invoices]
        self.assertEqual(amounts, sorted(amounts))

    def test_order_notifications_by_created_at(self):
        """Test ordering notifications by creation date."""
        response = self.client.get(reverse('list_notifications') + '?order_by=created_at')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/list_notifications.html')
        notifications = response.context['notifications']
        created_at_list = [notification.created_at for notification in notifications]
        self.assertEqual(created_at_list, sorted(created_at_list))

    # Searching Tests
    def test_search_users(self):
        """Test searching users."""
        response = self.client.get(reverse('list_users') + '?search=student')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/list_users.html')
        users = response.context['users']
        self.assertTrue(any('student' in user.username for user in users))

    def test_search_lessons(self):
        """Test searching lessons."""
        response = self.client.get(reverse('list_lessons') + '?search=Python')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/list_lessons.html')
        lessons = response.context['lessons']
        self.assertTrue(any('Python' in lesson.subject.name for lesson in lessons))

    def test_search_invoices(self):
        """Test searching invoices."""
        response = self.client.get(reverse('list_invoices') + '?search=charlie')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/list_invoices.html')
        invoices = response.context['invoices']
        self.assertTrue(any('charlie' in str(invoice.student) for invoice in invoices))

    def test_search_notifications(self):
        """Test searching notifications."""
        response = self.client.get(reverse('list_notifications') + '?search=test')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/list_notifications.html')
        notifications = response.context['notifications']
        self.assertTrue(any('test' in notification.message for notification in notifications))
