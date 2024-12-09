from django.test import TestCase
from tutorials.models import User
from libgravatar import Gravatar

class UserProfileDetailsTest(TestCase):
    """Detailed tests for user profile features."""

    def setUp(self):
        self.user = User.objects.create(
            username='@testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            type='student'
        )

    def test_first_name_exists(self):
        self.assertEqual(self.user.first_name, 'Test')

    def test_last_name_exists(self):
        self.assertEqual(self.user.last_name, 'User')

    def test_email_exists(self):
        self.assertEqual(self.user.email, 'test@example.com')

    def test_username_exists(self):
        self.assertEqual(self.user.username, '@testuser')

    def test_user_type_exists(self):
        self.assertEqual(self.user.type, 'student')

    def test_full_name_method_exists(self):
        self.assertTrue(hasattr(self.user, 'full_name'))

    def test_full_name_combines_first_and_last(self):
        self.assertEqual(self.user.full_name(), 'Test User')

    def test_gravatar_method_exists(self):
        self.assertTrue(hasattr(self.user, 'gravatar'))

    def test_mini_gravatar_method_exists(self):
        self.assertTrue(hasattr(self.user, 'mini_gravatar'))

    def test_default_gravatar_size_is_120(self):
        url = self.user.gravatar()
        self.assertIn('size=120', url)

    def test_custom_gravatar_size_50(self):
        url = self.user.gravatar(size=50)
        self.assertIn('size=50', url)

    def test_custom_gravatar_size_200(self):
        url = self.user.gravatar(size=200)
        self.assertIn('size=200', url)

    def test_mini_gravatar_size_is_60(self):
        url = self.user.mini_gravatar()
        self.assertIn('size=60', url)

    def test_gravatar_has_default_image(self):
        url = self.user.gravatar()
        self.assertIn('default=mp', url)

    def test_same_gravatar_for_same_email(self):
        url1 = self.user.gravatar()
        url2 = self.user.gravatar()
        self.assertEqual(url1, url2)