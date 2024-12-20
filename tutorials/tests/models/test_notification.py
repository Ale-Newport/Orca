from django.test import TestCase
from tutorials.models import User, Notification
from django.utils import timezone

class NotificationBasicsTest(TestCase):
    """Tests for the Notification model."""

    fixtures = ['tutorials/tests/fixtures/subjects.json', 'tutorials/tests/fixtures/users.json']

    def setUp(self):
        self.user = User.objects.get(pk=1)

    def test_notification_has_created_date(self):
        notification = Notification.objects.create(
            user=self.user,
            message="Test message"
        )
        self.assertIsNotNone(notification.created_at)
        self.assertTrue(isinstance(notification.created_at, type(timezone.now())))
        self.assertTrue(notification.created_at <= timezone.now())

    def test_notification_default_unread(self):
        notification = Notification.objects.create(
            user=self.user,
            message="Test message"
        )
        self.assertFalse(notification.is_read)

    def test_notification_mark_as_read(self):
        notification = Notification.objects.create(
            user=self.user,
            message="Test message"
        )
        notification.is_read = True
        notification.save()
        self.assertTrue(notification.is_read)

    def test_notification_string_shows_status(self):
        notification = Notification.objects.create(
            user=self.user,
            message="Test message"
        )
        self.assertIn('Unread', str(notification))
        notification.is_read = True
        notification.save()
        self.assertIn('Read', str(notification))

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


    def test_notification_with_long_message(self):
        long_message = "A" * 1024
        notification = Notification.objects.create(
            user=self.user,
            message=long_message
        )
        self.assertEqual(notification.message, long_message)

    def test_notification_with_empty_message(self):
        empty_message = ""
        notification = Notification.objects.create(
            user=self.user,
            message=empty_message
        )
        self.assertEqual(notification.message, empty_message)
