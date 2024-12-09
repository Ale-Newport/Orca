from django.test import TestCase
from tutorials.models import User

class GravatarTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='@testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            type='student',
            password='Password123'
        )

    def test_gravatar_url_contains_email_hash(self):
        gravatar_url = self.user.gravatar()
        self.assertIn('gravatar.com/avatar/', gravatar_url)

    def test_gravatar_size_parameter(self):
        test_size = 200
        gravatar_url = self.user.gravatar(size=test_size)
        self.assertIn(f'size={test_size}', gravatar_url)

    def test_mini_gravatar_size(self):
        mini_url = self.user.mini_gravatar()
        self.assertIn('size=60', mini_url)

    def test_gravatar_default_image(self):
        gravatar_url = self.user.gravatar()
        self.assertIn('default=mp', gravatar_url)

    def test_gravatar_url_is_https(self):
        gravatar_url = self.user.gravatar()
        self.assertTrue(gravatar_url.startswith('https://'))