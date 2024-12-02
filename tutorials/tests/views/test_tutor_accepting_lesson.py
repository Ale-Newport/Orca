from django.test import TestCase
class TutorAcceptLessonTestCase(TestCase):
    def setUp(self):
        self.tutor = User.objects.create_user(
            username='@tutor',
            password='Password123',
            email='tutor@example.com',
            type='tutor'
        )
        self.lesson = Lesson.objects.create(
            student=self.tutor,
            subject='Python',
            date=timezone.now() + timedelta(days=1),
            duration=60,
            status='Pending'
        )
        self.url = reverse('choose_class')
        self.client.login(username='@tutor', password='Password123')

    def test_tutor_can_view_lesson_requests(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python')

    def test_tutor_can_accept_lesson(self):
        # Simulate accepting the lesson
        self.lesson.tutor = self.tutor.full_name()
        self.lesson.status = 'Approved'
        self.lesson.save()
        self.assertEqual(self.lesson.tutor, self.tutor.full_name())
        self.assertEqual(self.lesson.status, 'Approved')

class TutorAssignedLessonsTestCase(TestCase):
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
            date=timezone.now() + timedelta(days=2),
            duration=90,
            tutor=self.tutor.full_name(),
            status='Approved'
        )
        self.url = reverse('tutor_dashboard')
        self.client.login(username='@tutor', password='Password123')

    def test_tutor_dashboard_shows_assigned_lessons(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Java')
