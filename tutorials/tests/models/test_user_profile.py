from django.test import TestCase
from django.db import IntegrityError
from tutorials.models import User


class UserProfileTest(TestCase):
    """Tests for user profile functionality."""

    def setUp(self):
        self.user = User.objects.create(
            username='@testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            type='student'
        )

    def test_gravatar_size_variations(self):
        """Test that gravatar URLs are generated with correct sizes."""
        test_sizes = [60, 120, 200, 300]
        for size in test_sizes:
            gravatar_url = self.user.gravatar(size=size)
            self.assertIn(f'size={size}', gravatar_url)
            self.assertIn('mp', gravatar_url)  # Default image parameter

    def test_mini_gravatar(self):
        """Test the mini gravatar shortcut method."""
        mini_url = self.user.mini_gravatar()
        self.assertIn('size=60', mini_url)

    def test_full_name_combinations(self):
        """Test full_name method with different name combinations."""
        name_combinations = [
            ('John', 'Doe', 'John Doe'),
            ('Mary', 'Smith-Jones', 'Mary Smith-Jones'),
            ('A', 'B', 'A B'),
            ('José', 'García', 'José García')
        ]
        
        for first, last, expected in name_combinations:
            self.user.first_name = first
            self.user.last_name = last
            self.user.save()
            self.assertEqual(self.user.full_name(), expected)

    def test_email_case_sensitivity(self):
        User.objects.create_user(
            username='@testuser1',
            email='test@example.com',
            password='Password123',
            first_name='Test',
            last_name='User',
            type='student'
        )
        # Attempt to create user with same email in different case
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='@testuser2',
                email='TEST@example.com',
                password='Password123',
                first_name='Test',
                last_name='User',
                type='student'
            )