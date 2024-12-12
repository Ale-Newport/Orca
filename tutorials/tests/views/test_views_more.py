from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Notification

class ViewsTestCase(TestCase):
    """Test cases to cover missing lines in views.py."""

    fixtures = ['tutorials/tests/fixtures/subjects.json', 'tutorials/tests/fixtures/users.json', 'tutorials/tests/fixtures/notifications.json']

    def setUp(self):
        """Set up test data and authenticate a user."""
        self.user = User.objects.get(pk=1)
        self.client.login(username=self.user.username, password='Password123')

    def test_home_view(self):
        """Test the home view."""
        self.client.logout()
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/home.html')

    def test_dashboard_redirects_based_on_user_type(self):
        """Test the dashboard redirection based on user type."""
        self.user.type = 'student'
        self.user.save()
        response = self.client.get(reverse('student_dashboard'))
        self.assertRedirects(response, '/log_in/?next=/student/dashboard/')

        self.user.type = 'tutor'
        self.user.save()
        response = self.client.get(reverse('tutor_dashboard'))
        self.assertRedirects(response, '/log_in/?next=/tutor/dashboard/')

        self.user.type = 'admin'
        self.user.save()
        response = self.client.get(reverse('admin_dashboard'))
        self.assertRedirects(response, '/log_in/?next=/admin/dashboard/')

    def test_login_prohibited_view(self):
        """Test views that prohibit logged-in users."""
        response = self.client.get(reverse('log_in'))
        self.assertRedirects(response, reverse('student_dashboard'))

        self.client.logout()
        response = self.client.get(reverse('log_in'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/log_in.html')



    def test_password_view_access(self):
        """Test access to the password view."""
        response = self.client.get(reverse('password'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/password.html')

    def test_notifications_view(self):
        """Test the notifications view."""
        response = self.client.get(reverse('notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/list_notifications.html')
        self.assertIn('notifications', response.context)

    def test_mark_notification_read(self):
        """Test marking a notification as read/unread."""
        notification = Notification.objects.create(user=self.user, message="Test notification.", is_read=False)
        response = self.client.post(reverse('mark_notification_read', args=[notification.id]))
        self.assertRedirects(response, reverse('notifications'))

        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

        response = self.client.post(reverse('mark_notification_read', args=[notification.id]))
        notification.refresh_from_db()
        self.assertFalse(notification.is_read)
