"""Tests of the home view."""
from django.test import TestCase
from django.urls import reverse
from tutorials.models import User

class HomeViewTestCase(TestCase):
    """Tests of the home view."""

    fixtures = ['tutorials/tests/fixtures/subjects.json', 'tutorials/tests/fixtures/users.json']

    def setUp(self):
        self.url = reverse('home')
        self.user = User.objects.get(pk=1)
    
    def test_home_url(self):
        self.assertEqual(self.url,'/')
    
    def test_get_home(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/home.html')
