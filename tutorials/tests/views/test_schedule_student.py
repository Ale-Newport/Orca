from django.test import TestCase
class StudentScheduleViewTestCase(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username='@student',
            password='Password123',
            email='student@example.com',
            type='student'
        )
        self.lesson = Lesson.objects.create(
            student=self.student,
            subject='Python',
            date=timezone.now(),
            duration=60,
            status='Approved'
        )
        self.url = reverse('view_schedule')
        self.client.login(username='@student', password='Password123')

    def test_view_schedule(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python')
