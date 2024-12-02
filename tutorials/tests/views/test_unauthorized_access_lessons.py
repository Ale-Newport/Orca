from django.test import TestCase
class UnauthorizedLessonUpdateTestCase(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username='@student',
            password='Password123',
            email='student@example.com',
            type='student'
        )
        self.other_student = User.objects.create_user(
            username='@otherstudent',
            password='Password123',
            email='otherstudent@example.com',
            type='student'
        )
        self.lesson = Lesson.objects.create(
            student=self.student,
            subject='Python',
            date=timezone.now() + timedelta(days=2),
            duration=60
        )
        self.url = reverse('update_lesson', args=[self.lesson.id])

    def test_other_student_cannot_update_lesson(self):
        self.client.login(username='@otherstudent', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_anonymous_user_cannot_update_lesson(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
