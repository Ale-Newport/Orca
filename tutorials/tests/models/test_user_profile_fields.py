from django.test import TestCase
from tutorials.models import User
from django.core.exceptions import ValidationError

class UserProfileFieldsTest(TestCase):
    """Tests for user profile field validation."""

    def setUp(self):
        self.user = User.objects.create_user(  # Using create_user instead of create
            username='@testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            type='student',
            password='Password123'
        )

    def test_first_name_max_length_valid(self):
        self.user.first_name = 'A' * 50
        try:
            self.user.clean_fields(exclude=['password'])  # Exclude password validation
            self.assertTrue(True)
        except ValidationError:
            self.fail("First name of max length should be valid")

    def test_last_name_max_length_valid(self):
        self.user.last_name = 'A' * 50
        try:
            self.user.clean_fields(exclude=['password'])
            self.assertTrue(True)
        except ValidationError:
            self.fail("Last name of max length should be valid")

    def test_username_starts_with_at(self):
        self.assertTrue(self.user.username.startswith('@'))

    def test_username_min_length_valid(self):
        self.user.username = '@abc'
        try:
            self.user.clean_fields(exclude=['password'])
            self.assertTrue(True)
        except ValidationError:
            self.fail("Username of minimum length should be valid")

    def test_email_contains_at_symbol(self):
        self.assertIn('@', self.user.email)

    def test_email_has_domain(self):
        self.assertIn('.com', self.user.email)

    def test_type_is_valid_choice(self):
        valid_types = ['student', 'tutor', 'admin']
        self.assertIn(self.user.type, valid_types)

    def test_empty_first_name_invalid(self):
        self.user.first_name = ''
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    def test_empty_last_name_invalid(self):
        self.user.last_name = ''
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    def test_empty_email_invalid(self):
        self.user.email = ''
        with self.assertRaises(ValidationError):
            self.user.full_clean()