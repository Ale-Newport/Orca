from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Notification

class NotificationViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='@testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            type='student',
            password='Password123'
        )
        self.notification = Notification.objects.create(
            user=self.user,
            message="Test notification"
        )

    def test_notifications_view_requires_login(self):
        url = reverse('notifications')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/log_in/'))

    def test_logged_in_user_can_see_notifications(self):
        self.client.login(username='@testuser', password='Password123')
        url = reverse('notifications')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/list_notifications.html')

    def test_user_can_mark_notification_read(self):
        self.client.login(username='@testuser', password='Password123')
        url = reverse('mark_notification_read', args=[self.notification.id])
        self.assertFalse(self.notification.is_read)
        response = self.client.get(url)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)

    def test_notifications_ordered_by_date(self):
        self.client.login(username='@testuser', password='Password123')
        Notification.objects.create(user=self.user, message="Second notification")
        url = reverse('notifications')
        response = self.client.get(url)
        notifications = response.context['notifications']
        self.assertTrue(notifications[0].created_at >= notifications[1].created_at)

    def test_user_only_sees_own_notifications(self):
        other_user = User.objects.create_user(
            username='@otheruser',
            email='other@example.com',
            first_name='Other',
            last_name='User',
            type='student',
            password='Password123'
        )
        Notification.objects.create(user=other_user, message="Other's notification")
        
        self.client.login(username='@testuser', password='Password123')
        url = reverse('notifications')
        response = self.client.get(url)
        notifications = response.context['notifications']
        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0], self.notification)