from django.test import TestCase
from tutorials.models import User

class UserTypeTest(TestCase):
    def test_create_student_user(self):
        user = User.objects.create(
            username='@student',
            email='student@example.com',
            first_name='Student',
            last_name='Test',
            type='student'
        )
        self.assertEqual(user.type, 'student')

    def test_create_tutor_user(self):
        user = User.objects.create(
            username='@tutor',
            email='tutor@example.com',
            first_name='Tutor',
            last_name='Test',
            type='tutor'
        )
        self.assertEqual(user.type, 'tutor')

    def test_create_admin_user(self):
        user = User.objects.create(
            username='@admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='Test',
            type='admin'
        )
        self.assertEqual(user.type, 'admin')

    def test_user_type_choices(self):
        self.assertIn(('student', 'Student'), User.USER_TYPE_CHOICES)
        self.assertIn(('tutor', 'Tutor'), User.USER_TYPE_CHOICES)
        self.assertIn(('admin', 'Admin'), User.USER_TYPE_CHOICES)

    def test_user_type_field_exists(self):
        user = User.objects.create(
            username='@testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            type='student'
        )
        self.assertTrue(hasattr(user, 'type'))