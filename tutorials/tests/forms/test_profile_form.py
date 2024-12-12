from django.test import TestCase
from django import forms
from tutorials.forms import ProfileForm
from tutorials.models import User, Subject

class ProfileFormTestCase(TestCase):
    """Unit tests for the ProfileForm."""

    fixtures = ['tutorials/tests/fixtures/subjects.json', 'tutorials/tests/fixtures/users.json']

    def setUp(self):
        """Set up test data."""
        self.tutor = User.objects.get(pk=2)
        self.student = User.objects.get(pk=1)
        self.subject = Subject.objects.get(pk=1)
        self.valid_data = {
            'username': '@new_username',
            'email': 'new_email@example.com',
            'first_name': 'NewFirstName',
            'last_name': 'NewLastName',
        }

    def test_form_contains_required_fields_for_student(self):
        """Test that the form contains the required fields for a student."""
        form = ProfileForm(instance=self.student)
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('username', form.fields)
        self.assertIn('email', form.fields)
        self.assertNotIn('subjects', form.fields)

    def test_form_contains_subjects_field_for_tutor(self):
        """Test that the form contains the 'subjects' field for a tutor."""
        form = ProfileForm(instance=self.tutor)
        self.assertIn('subjects', form.fields)
        self.assertIsInstance(form.fields['subjects'], forms.ModelMultipleChoiceField)
        self.assertEqual(form.fields['subjects'].queryset.count(), Subject.objects.count())

    def test_form_accepts_valid_input(self):
        """Test that the form accepts valid input."""
        form = ProfileForm(data=self.valid_data, instance=self.student)
        self.assertTrue(form.is_valid())

    def test_form_rejects_duplicate_username(self):
        """Test that the form rejects a duplicate username."""
        User.objects.create_user(username='duplicate_user', email='duplicate@example.com')
        self.valid_data['username'] = 'duplicate_user'
        form = ProfileForm(data=self.valid_data, instance=self.student)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertEqual(form.errors['username'], ['This username is already taken.'])

    def test_form_rejects_duplicate_email(self):
        """Test that the form rejects a duplicate email."""
        User.objects.create_user(username='other_user', email='duplicate@example.com')
        self.valid_data['email'] = 'duplicate@example.com'
        form = ProfileForm(data=self.valid_data, instance=self.student)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertEqual(form.errors['email'], ['This email is already taken.'])

    def test_form_allows_username_and_email_for_same_user(self):
        """Test that the form allows unchanged username and email for the same user."""
        self.valid_data['username'] = self.student.username
        self.valid_data['email'] = self.student.email
        form = ProfileForm(data=self.valid_data, instance=self.student)
        self.assertTrue(form.is_valid())

    def test_form_allows_subjects_for_tutor(self):
        """Test that the form allows assigning subjects to a tutor."""
        self.valid_data['subjects'] = [self.subject.id]
        form = ProfileForm(data=self.valid_data, instance=self.tutor)
        self.assertTrue(form.is_valid())

    def test_form_rejects_empty_subjects_for_tutor(self):
        """Test that the form rejects empty subjects for a tutor."""
        form = ProfileForm(data=self.valid_data, instance=self.tutor)
        self.valid_data['subjects'] = []
        form = ProfileForm(data=self.valid_data, instance=self.tutor)
        self.assertFalse(form.is_valid())
        self.assertIn('subjects', form.errors)
