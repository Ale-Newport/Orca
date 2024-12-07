from django.test import TestCase
from tutorials.models import User, Notification
from django.utils import timezone

class NotificationBasicsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='@testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            type='student'
        )

    def test_notification_has_created_date(self):
        notification = Notification.objects.create(
            user=self.user,
            message="Test message"
        )
        self.assertIsNotNone(notification.created_at)
        self.assertTrue(isinstance(notification.created_at, type(timezone.now())))

    def test_notification_default_unread(self):
        notification = Notification.objects.create(
            user=self.user,
            message="Test message"
        )
        self.assertFalse(notification.is_read)

    def test_notification_string_shows_status(self):
        notification = Notification.objects.create(
            user=self.user,
            message="Test message"
        )
        self.assertIn('Unread', str(notification))

    def test_notification_belongs_to_user(self):
        notification = Notification.objects.create(
            user=self.user,
            message="Test message"
        )
        self.assertEqual(notification.user, self.user)

    def test_notification_message_exists(self):
        test_message = "Test message"
        notification = Notification.objects.create(
            user=self.user,
            message=test_message
        )
        self.assertEqual(notification.message, test_message)