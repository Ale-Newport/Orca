from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Notification
from django.contrib.auth import get_user_model

User = get_user_model()

class UserManagementViewTestCase(TestCase):
    """Tests for user management views."""

    fixtures = ['tutorials/tests/fixtures/subjects.json', 'tutorials/tests/fixtures/users.json', 'tutorials/tests/fixtures/notifications.json']

    def setUp(self):
        """Set up test data."""
        self.student_user = User.objects.get(pk=1)
        self.tutor_user = User.objects.get(pk=2)
        self.admin_user = User.objects.get(pk=3)
        self.password = 'Password123'

        self.student_user.set_password(self.password)
        self.tutor_user.set_password(self.password)
        self.admin_user.set_password(self.password)

        self.student_user.save()
        self.tutor_user.save()
        self.admin_user.save()

    # Test for the home page
    def test_home_view(self):
        """Test the home page."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/home.html')

    # Log In View
    def test_log_in_view(self):
        """Test the log in view."""
        response = self.client.get(reverse('log_in'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/log_in.html')

        # Post valid credentials
        data = {'username': self.student_user.username, 'password': 'Password123'}
        response = self.client.post(reverse('log_in'), data)
        self.assertRedirects(response, reverse('student_dashboard'))

        # Post invalid credentials
        data = {'username': self.student_user.username, 'password': 'WrongPassword'}
        response = self.client.post(reverse('log_in'), data)
        self.assertEqual(response.status_code, 302)

    # Log Out View
    def test_log_out_view(self):
        """Test the log out view."""
        self.client.login(username=self.student_user.username, password=self.password)
        response = self.client.get(reverse('log_out'))
        self.assertRedirects(response, reverse('home'))

    # Password Change View
    def test_password_view_student(self):
        """Test the password change view."""
        self.client.login(username=self.student_user.username, password=self.password)
        response = self.client.get(reverse('password'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/password.html')

        # Post valid password change
        data = {
            'password': self.password,
            'new_password': 'NewPassword123',
            'password_confirmation': 'NewPassword123'
        }
        response = self.client.post(reverse('password'), data)
        self.assertRedirects(response, reverse('student_dashboard'))

    def test_password_view_tutor(self):
        """Test the password change view."""
        self.client.login(username=self.tutor_user.username, password=self.password)
        response = self.client.get(reverse('password'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/password.html')

        # Post valid password change
        data = {
            'password': self.password,
            'new_password': 'NewPassword123',
            'password_confirmation': 'NewPassword123'
        }
        response = self.client.post(reverse('password'), data)
        self.assertRedirects(response, reverse('tutor_dashboard'))

    def test_password_view_admin(self):
        """Test the password change view."""
        self.client.login(username=self.admin_user.username, password=self.password)
        response = self.client.get(reverse('password'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/password.html')

        # Post valid password change
        data = {
            'password': self.password,
            'new_password': 'NewPassword123',
            'password_confirmation': 'NewPassword123'
        }
        response = self.client.post(reverse('password'), data)
        self.assertRedirects(response, reverse('admin_dashboard'))

    # Profile Update View
    def test_profile_update_view_student(self):
        """Test the profile update view."""
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/profile.html')

        # Post valid profile update
        data = {
            'first_name': 'Updated',
            'last_name': 'User',
            'email': 'updatedstudent@example.com',
            'username': self.student_user.username,
        }
        response = self.client.post(reverse('profile'), data)
        self.assertRedirects(response, reverse('student_dashboard'))
        self.student_user.refresh_from_db()
        self.assertEqual(self.student_user.email, 'updatedstudent@example.com')

    def test_profile_update_view_tutor(self):
        """Test the profile update view."""
        self.client.login(username=self.tutor_user.username, password='Password123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/profile.html')

        # Post valid profile update
        data = {
            'first_name': 'Updated',
            'last_name': 'User',
            'email': 'updatedtutor@example.com',
            'username': self.tutor_user.username,
            'type': 'tutor',
            'subjects': [1, 2, 3, 4, 5]
        }
        response = self.client.post(reverse('profile'), data)
        self.assertRedirects(response, reverse('tutor_dashboard'))
        self.tutor_user.refresh_from_db()
        self.assertEqual(self.tutor_user.email, 'updatedtutor@example.com')

    def test_profile_update_view_admin(self):
        """Test the profile update view."""
        self.client.login(username=self.admin_user.username, password='Password123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/profile.html')

        # Post valid profile update
        data = {
            'first_name': 'Updated',
            'last_name': 'User',
            'email': 'updatedadmin@example.com',
            'username': self.admin_user.username,
        }
        response = self.client.post(reverse('profile'), data)
        self.assertRedirects(response, reverse('admin_dashboard'))
        self.admin_user.refresh_from_db()
        self.assertEqual(self.admin_user.email, 'updatedadmin@example.com')

    # Notifications View
    def test_notifications_view(self):
        """Test the notifications view."""
        self.client.login(username=self.student_user.username, password=self.password)
        response = self.client.get(reverse('notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/list_notifications.html')
        self.assertIn('notifications', response.context)

    # Mark Notification Read/Unread
    def test_mark_notification_read_view(self):
        """Test toggling notification read status."""
        self.client.login(username=self.student_user.username, password=self.password)
        notification = Notification.objects.filter(user=self.student_user).first()
        initial_status = notification.is_read

        response = self.client.post(reverse('mark_notification_read', args=[notification.id]))
        self.assertRedirects(response, reverse('notifications'))
        notification.refresh_from_db()
        self.assertEqual(notification.is_read, not initial_status)

    # Sign Up View
    def test_sign_up_view(self):
        """Test the sign up view."""
        response = self.client.get(reverse('sign_up'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/sign_up.html')

        # Post valid sign-up data
        data = {
            'username': '@new_user',
            'new_password': 'NewPassword123',
            'password_confirmation': 'NewPassword123',
            'email': 'new_user@example.com',
            'type': 'student',
            'first_name': 'Test',
            'last_name': 'User',
        }
        response = self.client.post(reverse('sign_up'), data)
        self.assertRedirects(response, reverse('student_dashboard'))
        self.assertTrue(User.objects.filter(username='@new_user').exists())

    # LoginProhibitedMixin Handling
    def test_login_prohibited_mixin_redirects_logged_in_users(self):
        """Test that logged-in users are redirected from login-prohibited views."""
        self.client.login(username=self.student_user.username, password=self.password)
        response = self.client.get(reverse('sign_up'))
        self.assertRedirects(response, reverse('student_dashboard'))
