from django.test import TestCase
from django.urls import reverse
from tutorials.models import User

class ViewPermissionsTest(TestCase):
    fixtures = ['tutorials/tests/fixtures/subjects.json', 'tutorials/tests/fixtures/users.json']

    def setUp(self):
        self.student = User.objects.get(pk=1)
        self.tutor = User.objects.get(pk=2)

    def test_student_cannot_access_tutor_dashboard(self):
        self.client.login(username=self.student.username, password='Password123')
        url = reverse('tutor_dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_tutor_cannot_access_student_dashboard(self):
        self.client.login(username=self.tutor.username, password='Password123')
        url = reverse('student_dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_logout_redirects_to_home(self):
        self.client.login(username=self.student.username, password='Password123')
        url = reverse('log_out')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('home'))

    def test_user_cannot_access_profile_without_login(self):
        url = reverse('profile')
        response = self.client.get(url)
        expected_url = f"{reverse('log_in')}?next={url}"
        self.assertRedirects(response, expected_url)

    def test_user_cannot_access_password_change_without_login(self):
        url = reverse('password')
        response = self.client.get(url)
        expected_url = f"{reverse('log_in')}?next={url}"
        self.assertRedirects(response, expected_url)