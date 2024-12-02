from django.test import TestCase

class UpcomingLessonsViewTestCase(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username='@student',
            password='Password123',
            email='student@example.com',
            type='student'
        )
        self.lesson1 = Lesson.objects.create(
            student=self.student,
            subject='Python',
            date=timezone.now() + timedelta(days=1),
            duration=60,
            status='Approved'
        )
        self.lesson2 = Lesson.objects.create(
            student=self.student,
            subject='Java',
            date=timezone.now() + timedelta(days=2),
            duration=90,
            status='Pending'
        )
        self.url = reverse('view_upcoming_lessons')
        self.client.login(username='@student', password='Password123')

    def test_view_upcoming_lessons(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python')
        self.assertNotContains(response, 'Java')  # Only approved lessons should be shown
