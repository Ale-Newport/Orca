from django.contrib.auth.hashers import check_password
from django import forms
from django.test import TestCase
from tutorials.forms import SignUpForm
from tutorials.models import User

class SignUpFormTestCase(TestCase):
    """Unit tests of the sign up form."""

    def setUp(self):
        self.form_input = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'username': '@janedoe',
            'email': 'janedoe@example.org',
            'new_password': 'Password123',
            'password_confirmation': 'Password123',
            'type': 'student'
        }

    def test_valid_sign_up_form(self):
        form_input = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'username': '@janedoe2',  # Ensure unique username
            'email': 'janedoe2@example.org',  # Ensure unique email
            'new_password': 'Password123',
            'password_confirmation': 'Password123',
            'type': 'student'
        }
        form = SignUpForm(data=form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = SignUpForm()
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('username', form.fields)
        self.assertIn('email', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))
        self.assertIn('new_password', form.fields)
        new_password_widget = form.fields['new_password'].widget
        self.assertTrue(isinstance(new_password_widget, forms.PasswordInput))
        self.assertIn('password_confirmation', form.fields)
        password_confirmation_widget = form.fields['password_confirmation'].widget
        self.assertTrue(isinstance(password_confirmation_widget, forms.PasswordInput))

    def test_form_uses_model_validation(self):
        self.form_input['username'] = 'badusername'
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_uppercase_character(self):
        self.form_input['new_password'] = 'password123'
        self.form_input['password_confirmation'] = 'password123'
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_lowercase_character(self):
        self.form_input['new_password'] = 'PASSWORD123'
        self.form_input['password_confirmation'] = 'PASSWORD123'
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_number(self):
        self.form_input['new_password'] = 'PasswordABC'
        self.form_input['password_confirmation'] = 'PasswordABC'
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_new_password_and_password_confirmation_are_identical(self):
        self.form_input['password_confirmation'] = 'WrongPassword123'
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        """Test that form saves user correctly with valid data."""
        form = SignUpForm(data={
            'first_name': 'Jane',
            'last_name': 'Doe',
            'username': '@janedoe3',
            'email': 'janedoe3@example.org',
            'new_password': 'Password123',
            'password_confirmation': 'Password123',
            'type': 'student'
        })
        self.assertTrue(form.is_valid())
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count + 1)