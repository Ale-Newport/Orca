from django.test import TestCase
from django.urls import reverse

class HomePageTest(TestCase):
    def test_home_page_returns_correct_response(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_home_page_accessible_without_login(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_page_uses_correct_template(self):
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home.html')

    def test_home_page_contains_sign_up_link(self):
        response = self.client.get(reverse('home'))
        signup_url = reverse('sign_up')
        self.assertContains(response, signup_url)

    def test_home_page_contains_login_link(self):
        response = self.client.get(reverse('home'))
        login_url = reverse('log_in')
        self.assertContains(response, login_url)