from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Lesson, Invoice, Notification, Subject
from datetime import date, timedelta
from django.utils import timezone

class AdminViewTestCase(TestCase):
    """Tests for the admin views."""

    fixtures = ['tutorials/tests/fixtures/subjects.json', 'tutorials/tests/fixtures/users.json', 'tutorials/tests/fixtures/lessons.json', 'tutorials/tests/fixtures/invoices.json', 'tutorials/tests/fixtures/notifications.json']

    def setUp(self):
        """Set up test data and authenticate the admin user."""
        self.admin_user = User.objects.get(pk=3)
        self.client.login(username=self.admin_user.username, password='Password123')

    def test_dashboard_view(self):
        """Test the admin dashboard view."""
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/admin_dashboard.html')
        self.assertIn('total_users', response.context)

    def test_list_users_view(self):
        """Test the list users view."""
        response = self.client.get(reverse('list_users'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/list_users.html')
        self.assertIn('users', response.context)

    def test_create_user_view(self):
        """Test the create/update user view."""
        response = self.client.get(reverse('create_user'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/create_update_user.html')
        self.assertIn('form', response.context)

        # Test creating a user
        data = {
            'username': '@new_user',
            'email': 'new_user@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'type': 'student'
        }
        response = self.client.post(reverse('create_user'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='@new_user').exists())
    
    def test_create_user_view_fail(self):
        """Test the create/update user view."""
        response = self.client.get(reverse('create_user'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/create_update_user.html')
        self.assertIn('form', response.context)

        # Test creating a user
        data = {
            'username': 'new_user', # Invalid username
            'email': 'new_user@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'type': 'student'
        }
        response = self.client.post(reverse('create_user'), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('username', response.context['form'].errors)
    
    def test_update_user_view(self):
        """Test the create/update user view."""
        response = self.client.get(reverse('update_user', args=[self.admin_user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/create_update_user.html')
        self.assertIn('form', response.context)

        # Test creating a user
        data = {
            'username': '@updated_user',
            'email': 'updated_user@example.com',
            'first_name': 'Updated',
            'last_name': 'User',
            'type': 'student'
        }
        response = self.client.post(reverse('update_user', args=[self.admin_user.id]), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='@updated_user').exists())

    def test_list_lessons_view(self):
        """Test the list lessons view."""
        response = self.client.get(reverse('list_lessons'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/list_lessons.html')
        self.assertIn('lessons', response.context)

    def test_create_lesson_view(self):
        """Test the create/update lesson view."""
        response = self.client.get(reverse('create_lesson'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/create_update_lesson.html')
        self.assertIn('form', response.context)

        # Test creating a lesson
        student = User.objects.filter(type='student').first()
        tutor = User.objects.filter(type='tutor').first()
        subject = Subject.objects.first()
        data = {
            'student': student.id,
            'subject': subject.id,
            'tutor': tutor.id,
            'date': timezone.now() + timedelta(days=1),
            'duration': 60,
            'status': 'Approved',
            'recurrence': 'None',
        }
        response = self.client.post(reverse('create_lesson'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Lesson.objects.filter(student=student, subject=subject).exists())

    def test_create_lesson_view_fail(self):
        """Test the create/update lesson view."""
        response = self.client.get(reverse('create_lesson'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/create_update_lesson.html')
        self.assertIn('form', response.context)

        # Test creating a lesson
        student = User.objects.filter(type='student').first()
        tutor = User.objects.filter(type='tutor').first()
        subject = Subject.objects.first()
        data = {
            'student': student.id,
            'subject': subject.id,
            'tutor': tutor.id,
            'date': timezone.now() + timedelta(days=1),
            'duration': 61, # Invalid duration
            'status': 'Approved',
            'recurrence': 'None',
        }
        response = self.client.post(reverse('create_lesson'), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('duration', response.context['form'].errors)

    def test_update_lesson_view(self):
        """Test the create/update lesson view."""
        lesson = Lesson.objects.first()
        response = self.client.get(reverse('update_lesson', args=[lesson.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/create_update_lesson.html')
        self.assertIn('form', response.context)

        # Test creating a lesson
        student = User.objects.filter(type='student').first()
        tutor = User.objects.filter(type='tutor').first()
        subject = Subject.objects.first()
        data = {
            'student': student.id,
            'subject': subject.id,
            'tutor': tutor.id,
            'date': timezone.now() + timedelta(days=1),
            'duration': 45,
            'status': 'Approved',
            'recurrence': 'None',
        }
        response = self.client.post(reverse('update_lesson', args=[lesson.id]), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Lesson.objects.filter(student=student, subject=subject).exists())

    def test_list_invoices_view(self):
        """Test the list invoices view."""
        response = self.client.get(reverse('list_invoices'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/list_invoices.html')
        self.assertIn('invoices', response.context)

    def test_create_invoice_view(self):
        """Test the create/update invoice view."""
        response = self.client.get(reverse('create_invoice'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/create_update_invoice.html')
        self.assertIn('form', response.context)

        # Test creating an invoice
        student = User.objects.filter(type='student').first()
        data = {
            'student': student.id,
            'amount': 100.00,
            'due_date': date.today() + timedelta(days=7),
            'paid': False,
        }
        response = self.client.post(reverse('create_invoice'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Invoice.objects.filter(student=student).exists())

    def test_create_invoice_view_fail(self):
        """Test the create/update invoice view."""
        response = self.client.get(reverse('create_invoice'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/create_update_invoice.html')
        self.assertIn('form', response.context)

        # Test creating an invoice
        student = User.objects.filter(type='student').first()
        data = {
            'student': student.id,
            'amount': -100.00,
            'due_date': date.today() + timedelta(days=7),
            'paid': False,
        }
        response = self.client.post(reverse('create_invoice'), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('amount', response.context['form'].errors)
    
    def test_update_invoice_view(self):
        """Test the create/update invoice view."""
        invoice = Invoice.objects.first()
        response = self.client.get(reverse('update_invoice', args=[invoice.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/create_update_invoice.html')
        self.assertIn('form', response.context)

        # Test creating an invoice
        student = User.objects.filter(type='student').first()
        data = {
            'student': student.id,
            'amount': 101.00,
            'due_date': date.today() + timedelta(days=7),
            'paid': False,
        }
        response = self.client.post(reverse('update_invoice', args=[invoice.id]), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Invoice.objects.filter(student=student).exists())

    def test_invoice_initial_data(self):
        """Test initial data creation based on model_name and pk."""
        # Test with Lesson
        lesson = Lesson.objects.first()
        response = self.client.get(reverse('create_invoice') + f'?model=Lesson&pk={lesson.id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/create_update_invoice.html')
        self.assertIn('student', response.context['form'].initial)
        self.assertIn('lesson', response.context['form'].initial)

        # Test with User
        user = User.objects.filter(type='student').first()
        response = self.client.get(reverse('create_invoice') + f'?model=User&pk={user.id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/create_update_invoice.html')
        self.assertIn('student', response.context['form'].initial)

        # Test with Notification
        notification = Notification.objects.first()
        response = self.client.get(reverse('create_invoice') + f'?model=Notification&pk={notification.id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/create_update_invoice.html')
        self.assertIn('student', response.context['form'].initial)

        # Test with Invoice
        invoice = Invoice.objects.first()
        response = self.client.get(reverse('create_invoice') + f'?model=Invoice&pk={invoice.id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/create_update_invoice.html')
        self.assertIn('form', response.context)

        # Test with invalid model
        response = self.client.get(reverse('create_invoice') + '?model=InvalidModel&pk=1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/create_update_invoice.html')
        self.assertIn('form', response.context)

    def test_list_notifications_view(self):
        """Test the list notifications view."""
        response = self.client.get(reverse('list_notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/list_notifications.html')
        self.assertIn('notifications', response.context)

    def test_create_notification_view(self):
        """Test the create notification view."""
        response = self.client.get(reverse('create_notification'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/create_notification.html')
        self.assertIn('form', response.context)

        # Test creating a notification
        user = User.objects.filter(type='student').first()
        data = {
            'user': user.id,
            'message': "This is a test notification.",
            'created_at': timezone.now(),
            'is_read': False,
        }
        response = self.client.post(reverse('create_notification'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Notification.objects.filter(user=user, message='This is a test notification.').exists())

    def test_create_notification_view_fail(self):
        """Test the create notification view."""
        response = self.client.get(reverse('create_notification'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/create_notification.html')
        self.assertIn('form', response.context)

        # Test creating a notification
        user = User.objects.filter(type='student').first()
        data = {
            'user': user.id,
            'message': "", # Invalid message
            'created_at': timezone.now(),
            'is_read': False,
        }
        response = self.client.post(reverse('create_notification'), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('message', response.context['form'].errors)

    def test_create_notification_with_invoice(self):
        """Test notification creation logic based on invoice."""
        # Test with Invoice
        invoice = Invoice.objects.filter(paid=True).first()
        response = self.client.get(reverse('create_notification') + f'?model=Invoice&pk={invoice.id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/create_notification.html')
        self.assertIn('user', response.context['form'].initial)
        self.assertIn('message', response.context['form'].initial)
        invoice = Invoice.objects.filter(paid=False, due_date__lte=timezone.now()).first()
        response = self.client.get(reverse('create_notification') + f'?model=Invoice&pk={invoice.id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/create_notification.html')
        self.assertIn('user', response.context['form'].initial)
        self.assertIn('message', response.context['form'].initial)
        invoice = Invoice.objects.filter(paid=False, due_date__gte=timezone.now()).first()
        response = self.client.get(reverse('create_notification') + f'?model=Invoice&pk={invoice.id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/create_notification.html')
        self.assertIn('user', response.context['form'].initial)
        self.assertIn('message', response.context['form'].initial)

    def test_create_notification_with_lesson(self):
        """Test notification creation logic based on lesson."""
        # Test with Lesson
        lesson = Lesson.objects.filter(status="Approved").exclude(tutor=None).first()
        response = self.client.get(reverse('create_notification') + f'?model=Lesson&pk={lesson.id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/create_notification.html')
        self.assertIn('user', response.context['form'].initial)
        self.assertIn('message', response.context['form'].initial)
        lesson = Lesson.objects.filter(status="Approved", tutor=None).first()
        response = self.client.get(reverse('create_notification') + f'?model=Lesson&pk={lesson.id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/create_notification.html')
        self.assertIn('user', response.context['form'].initial)
        self.assertIn('message', response.context['form'].initial)
        lesson = Lesson.objects.filter(status="Pending").first()
        response = self.client.get(reverse('create_notification') + f'?model=Lesson&pk={lesson.id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/create_notification.html')
        self.assertIn('user', response.context['form'].initial)
        self.assertIn('message', response.context['form'].initial)
        lesson = Lesson.objects.filter(status="Rejected").first()
        response = self.client.get(reverse('create_notification') + f'?model=Lesson&pk={lesson.id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/create_notification.html')
        self.assertIn('user', response.context['form'].initial)
        self.assertIn('message', response.context['form'].initial)

    def test_create_notification_with_user(self):
        """Test notification creation logic based on User."""
        # Test with User
        user = User.objects.filter(type='student').first()
        response = self.client.get(reverse('create_notification') + f'?model=User&pk={user.id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/create_notification.html')
        self.assertIn('user', response.context['form'].initial)
        self.assertEqual(response.context['form'].initial['message'], '')

        # Test with Notification
        notification = Notification.objects.first()
        response = self.client.get(reverse('create_notification') + f'?model=Notification&pk={notification.id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/create_notification.html')
        self.assertIn('form', response.context)

        # Test with invalid model
        response = self.client.get(reverse('create_notification') + '?model=InvalidModel&pk=1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/create_notification.html')
        self.assertIn('form', response.context)

    def test_delete_object_view(self):
        """Test the delete object view."""
        notification = Notification.objects.first()
        response = self.client.post(reverse('delete_object', args=['Notification', notification.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Notification.objects.filter(id=notification.id).exists())