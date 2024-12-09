from django.test import TestCase
from tutorials.models import User
from django.core.exceptions import ValidationError

class UserProfileValidationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='@testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            type='student',
            password='Password123'
        )

    def test_username_contains_at_symbol(self):
        self.assertTrue(self.user.username.startswith('@'))

    def test_username_alphanumeric_after_at(self):
        username_part = self.user.username[1:]
        self.assertTrue(username_part.isalnum())

    def test_user_has_type(self):
        self.assertIn(self.user.type, ['student', 'tutor', 'admin'])

    def test_email_contains_at_symbol(self):
        self.assertIn('@', self.user.email)

    def test_full_name_combines_correctly(self):
        expected_name = f"{self.user.first_name} {self.user.last_name}"
        self.assertEqual(self.user.full_name(), expected_name)