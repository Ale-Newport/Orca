from django.test import TestCase
class LessonStatusPermissionTestCase(TestCase):
    def setUp(self):
        self.student1 = User.objects.create_user(
            username='@student1',
            password='Password123',
            email='student1@example.com',
            type='student'
        )
        self.student2 = User.objects.create_user(
            username='@student2',
            password='Password123',
            email='student2@example.com',
            type='student'
        )
        self.lesson = Lesson.objects.create(
            student=self.student1,
            subject='Python',
            date=timezone.now() + timedelta(days=1),
            duration=60
        )
        self.url = reverse('update_lesson', args=[self.lesson.id])

    def test_student_cannot_edit_another_students_lesson(self):
        self.client.login(username='@student2', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
