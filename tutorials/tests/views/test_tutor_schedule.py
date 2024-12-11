from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Lesson, Subject
from django.utils import timezone
from datetime import timedelta

class TutorScheduleTest(TestCase):

    fixtures = ['tutorials/tests/fixtures/subjects.json', 'tutorials/tests/fixtures/users.json']

    def setUp(self):
        self.tutor = User.objects.get(pk=2)
        self.client.login(username=self.tutor.username, password='Password123')

    def test_schedule_shows_current_month(self):
        url = reverse('tutor_schedule')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        current_month = timezone.now().month
        self.assertIn(str(current_month), str(response.context['month']))

    def test_schedule_can_navigate_months(self):
        next_month = timezone.now().month + 1
        next_year = timezone.now().year
        if next_month > 12:
            next_month = 1
            next_year += 1
        url = reverse('tutor_schedule', kwargs={'year': next_year, 'month': next_month})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_schedule_shows_calendar(self):
        url = reverse('tutor_schedule')
        response = self.client.get(url)
        self.assertIn('calendar', response.context)

    def test_schedule_contains_lesson_info(self):
        url = reverse('tutor_schedule')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor/tutor_schedule.html')

    def test_schedule_shows_working_hours(self):
        future_date = timezone.now() + timedelta(days=1)
        Lesson.objects.create(
            tutor=self.tutor,
            student=User.objects.get(pk=1),
            subject=Subject.objects.get(pk=1),
            date=future_date.replace(hour=14),
            duration=60,
        )
        url = reverse('tutor_schedule')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)