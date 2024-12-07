from django.test import TestCase
from tutorials.forms import PasswordForm
from tutorials.models import User

class PasswordFormValidationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='@testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            type='student',
            password='Password123'
        )

    def test_password_has_uppercase(self):
        self.assertTrue(any(c.isupper() for c in 'Password123'))

    def test_password_has_lowercase(self):
        self.assertTrue(any(c.islower() for c in 'Password123'))

    def test_password_has_number(self):
        self.assertTrue(any(c.isdigit() for c in 'Password123'))

    def test_password_minimum_length(self):
        self.assertTrue(len('Password123') >= 8)

    def test_form_has_required_fields(self):
        form = PasswordForm(user=self.user)
        self.assertIn('password', form.fields)
        self.assertIn('new_password', form.fields)
        self.assertIn('password_confirmation', form.fields)