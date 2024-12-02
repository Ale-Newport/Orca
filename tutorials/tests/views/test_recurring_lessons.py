from django.test import TestCase
class RecurringLessonTestCase(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username='@student',
            password='Password123',
            email='student@example.com',
            type='student'
        )
        self.url = reverse('request_lesson')
        self.client.login(username='@student', password='Password123')

    def test_create_weekly_recurring_lessons(self):
        data = {
            'subject': 'Python',
            'preferred_date': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'),
            'duration': 60,
            'recurrence': 'Weekly',
            'end_date': (timezone.now() + timedelta(weeks=4)).strftime('%Y-%m-%d')
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        lessons = Lesson.objects.filter(student=self.student, subject='Python')
        self.assertEqual(lessons.count(), 5)  # Initial plus 4 recurrences

    def test_recurring_lessons_without_end_date(self):
        data = {
            'subject': 'Python',
            'preferred_date': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'),
            'duration': 60,
            'recurrence': 'Weekly',
            'end_date': ''  # Missing end date
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'end_date', 'Please enter an end date for the recurrence.')
