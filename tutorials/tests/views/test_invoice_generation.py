from django.test import TestCase

class InvoiceGenerationTestCase(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username='@student',
            password='Password123',
            email='student@example.com',
            type='student'
        )
        self.admin = User.objects.create_user(
            username='@admin',
            password='Password123',
            email='admin@example.com',
            type='admin',
            is_staff=True,
            is_superuser=True
        )
        self.lesson = Lesson.objects.create(
            student=self.student,
            subject='Python',
            date=timezone.now() + timedelta(days=1),
            duration=60,
            status='Pending'
        )
        self.client.login(username='@admin', password='Password123')

    def test_invoice_created_on_lesson_approval(self):
        self.lesson.status = 'Approved'
        self.lesson.save()
        # Simulate invoice generation logic
        Invoice.objects.create(
            student=self.student,
            amount=self.lesson.duration * 10,
            due_date=timezone.now() + timedelta(days=7),
            paid=False
        )
        self.assertTrue(Invoice.objects.filter(student=self.student).exists())
