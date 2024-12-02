from django.test import TestCase
class LessonRemoveTestCase(TestCase):
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
            date=timezone.now() + timedelta(days=2),
            duration=60
        )
        self.url = reverse('remove_lesson', args=[self.lesson.id])
        self.client.login(username='@student', password='Password123')

    def test_get_remove_lesson_confirmation(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'confirm_delete_lesson.html')

    def test_post_remove_lesson(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Lesson.objects.filter(id=self.lesson.id).exists())
