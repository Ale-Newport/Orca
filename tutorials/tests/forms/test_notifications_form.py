from django.test import TestCase
from tutorials.forms import NotificationForm
from tutorials.models import User, Notification

class NotificationFormTestCase(TestCase):
    """Unit tests for the NotificationForm."""

    fixtures = ['tutorials/tests/fixtures/subjects.json', 'tutorials/tests/fixtures/users.json']


    def setUp(self):
        """Set up test data."""
        self.user = User.objects.get(pk=1)
        self.valid_data = {
            'user': self.user,
            'message': 'This is a test notification.',
        }

    def test_form_contains_required_fields(self):
        """Test that the form contains the required fields."""
        form = NotificationForm()
        self.assertIn('user', form.fields)
        self.assertIn('message', form.fields)

    def test_form_accepts_valid_input(self):
        """Test that the form accepts valid input."""
        form = NotificationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_form_rejects_empty_message(self):
        """Test that the form rejects an empty message."""
        self.valid_data['message'] = ''
        form = NotificationForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)
        self.assertEqual(form.errors['message'], ['This field is required.', 'The message cannot be empty.'])

    def test_form_rejects_missing_user(self):
        """Test that the form rejects missing user."""
        self.valid_data.pop('user')
        form = NotificationForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('user', form.errors)

    def test_form_rejects_missing_message(self):
        """Test that the form rejects missing message."""
        self.valid_data.pop('message')
        form = NotificationForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)
