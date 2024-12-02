from django.test import TestCase

class InvoiceViewTestCase(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username='@student',
            password='Password123',
            email='student@example.com',
            type='student'
        )
        self.invoice_paid = Invoice.objects.create(
            student=self.student,
            amount=100.00,
            due_date=timezone.now() + timedelta(days=7),
            paid=True
        )
        self.invoice_unpaid = Invoice.objects.create(
            student=self.student,
            amount=150.00,
            due_date=timezone.now() + timedelta(days=14),
            paid=False
        )
        self.url = reverse('invoices')
        self.client.login(username='@student', password='Password123')

    def test_view_invoices(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '$100.00')
        self.assertContains(response, '$150.00')
        self.assertContains(response, 'Paid')
        self.assertContains(response, 'Unpaid')
