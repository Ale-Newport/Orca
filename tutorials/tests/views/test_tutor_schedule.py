from django.test import TestCase
class TutorScheduleViewTestCase(TestCase):
    def setUp(self):
        self.tutor = User.objects.create_user(
            username='@tutor',
            password='Password123',
            email='tutor@example.com',
            type='tutor'
        )
        self.lesson = Lesson.objects.create(
            student=self.tutor,
            subject='Java',
            date=timezone.now(),
            duration=60,
            status='Approved',
            tutor=self.tutor.full_name()
        )
        self.url = reverse('tutor_schedule')
        self.client.login(username='@tutor', password='Password123')

    def test_view_tutor_schedule(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Java')
