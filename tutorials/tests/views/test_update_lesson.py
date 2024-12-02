from django.test import TestCase
class LessonUpdateTestCase(TestCase):
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
            duration=60,
            tutor='Unknown Tutor',
            status='Pending'
        )
        self.url = reverse('update_lesson', args=[self.lesson.id])
        self.client.login(username='@student', password='Password123')

    def test_get_update_lesson_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update_lesson.html')

    def test_post_valid_lesson_update(self):
        data = {
            'subject': 'Java',
            'date': (timezone.now() + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M'),
            'duration': 90,
            'notes': 'Update notes.'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.subject, 'Java')
        self.assertEqual(self.lesson.duration, 90)
        self.assertEqual(self.lesson.notes, 'Update notes.')

    def test_post_invalid_lesson_update(self):
        data = {
            'subject': '',
            'date': '',
            'duration': '',
            'notes': ''
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'subject', 'This field is required.')
        self.assertFormError(response, 'form', 'date', 'This field is required.')
        self.assertFormError(response, 'form', 'duration', 'This field is required.')
