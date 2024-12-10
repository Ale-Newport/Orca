from django.test import TestCase
from tutorials.forms import PasswordForm
from tutorials.models import User

class PasswordFormValidationTest(TestCase):
    """Unit tests validator of the password form."""

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
        password = self.user.password
        self.assertTrue(any(c.isupper() for c in password), "Password should have at least one uppercase letter.")

    def test_password_has_lowercase(self):
        password = self.user.password
        self.assertTrue(any(c.islower() for c in password), "Password should have at least one lowercase letter.")

    def test_password_has_number(self):
        password = self.user.password
        self.assertTrue(any(c.isdigit() for c in password), "Password should have at least one number.")

    def test_password_minimum_length(self):
        password = self.user.password
        self.assertTrue(len(password) >= 8, "Password should be at least 8 characters long.")

    def test_form_has_required_fields(self):
        form = PasswordForm(user=self.user)
        self.assertIn('password', form.fields, "Form should include the 'password' field.")
        self.assertIn('new_password', form.fields, "Form should include the 'new_password' field.")
        self.assertIn('password_confirmation', form.fields, "Form should include the 'password_confirmation' field.")

    def test_invalid_password(self):
        form_data = {
            'password': 'short',
            'new_password': '123456',
            'password_confirmation': '123456'
        }
        form = PasswordForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid(), "Form should not be valid with an invalid password.")
        self.assertIn('password', form.errors, "Form should raise an error for invalid password.")

    def test_password_mismatch(self):
        form_data = {
            'password': 'Password123',
            'new_password': 'NewPassword123',
            'password_confirmation': 'Mismatch123'
        }
        form = PasswordForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid(), "Form should not be valid if passwords do not match.")
        self.assertIn('password_confirmation', form.errors, "Form should raise an error for password mismatch.")
