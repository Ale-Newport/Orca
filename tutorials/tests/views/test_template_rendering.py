from django.test import TestCase
from django.urls import reverse
from tutorials.models import User

class TemplateRenderingTest(TestCase):
    fixtures = ['tutorials/tests/fixtures/subjects.json', 'tutorials/tests/fixtures/users.json']

    def setUp(self):
        self.user = User.objects.get(pk=1)

    def test_login_page_uses_correct_template(self):
        response = self.client.get(reverse('log_in'))
        self.assertTemplateUsed(response, 'profile/log_in.html')

    def test_signup_page_uses_correct_template(self):
        response = self.client.get(reverse('sign_up'))
        self.assertTemplateUsed(response, 'profile/sign_up.html')

    def test_login_page_contains_form(self):
        response = self.client.get(reverse('log_in'))
        self.assertContains(response, '<form')
        self.assertContains(response, 'method="post"')

    def test_signup_page_contains_form(self):
        response = self.client.get(reverse('sign_up'))
        self.assertContains(response, '<form')
        self.assertContains(response, 'method="post"')

    def test_password_page_requires_login(self):
        response = self.client.get(reverse('password'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/log_in/'))