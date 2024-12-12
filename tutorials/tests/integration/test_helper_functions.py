from django.test import TestCase
from django.http import HttpRequest
from django.contrib.auth.models import AnonymousUser
from tutorials.models import User, Lesson, Subject
from tutorials.helpers import calculate_lesson_dates, days_between, calculate_invoice_amount, model_is_valid, login_prohibited
from datetime import datetime, timedelta, date
from django.utils import timezone
import pytz


class HelperFunctionsTestCase(TestCase):
    """Tests for helper functions."""

    fixtures = ['tutorials/tests/fixtures/subjects.json', 'tutorials/tests/fixtures/users.json', 'tutorials/tests/fixtures/lessons.json']

    def test_calculate_lesson_dates_none_recurrence(self):
        """Test calculate_lesson_dates with no recurrence."""
        start_date = timezone.now()
        end_date = timezone.now().date()
        recurrence = 'None'
        dates = calculate_lesson_dates(start_date, end_date, recurrence)
        self.assertEqual(dates, [start_date])

    def test_calculate_lesson_dates_daily_recurrence(self):
        """Test calculate_lesson_dates with daily recurrence."""
        start_date = datetime(2024, 1, 1, 10, 0, tzinfo=pytz.UTC)
        end_date = date(2024, 1, 3)
        recurrence = 'Daily'
        dates = calculate_lesson_dates(start_date, end_date, recurrence)
        self.assertEqual(dates, [
            datetime(2024, 1, 1, 10, 0, tzinfo=pytz.UTC),
            datetime(2024, 1, 2, 10, 0, tzinfo=pytz.UTC),
            datetime(2024, 1, 3, 10, 0, tzinfo=pytz.UTC),
        ])
    
    def test_calculate_lesson_dates_weekly_recurrence(self):
        """Test calculate_lesson_dates with daily recurrence."""
        start_date = datetime(2024, 1, 1, 10, 0, tzinfo=pytz.UTC)
        end_date = date(2024, 1, 18)
        recurrence = 'Weekly'
        dates = calculate_lesson_dates(start_date, end_date, recurrence)
        self.assertEqual(dates, [
            datetime(2024, 1, 1, 10, 0, tzinfo=pytz.UTC),
            datetime(2024, 1, 8, 10, 0, tzinfo=pytz.UTC),
            datetime(2024, 1, 15, 10, 0, tzinfo=pytz.UTC),
        ])

    def test_calculate_lesson_dates_monthly_recurrence(self):
        """Test calculate_lesson_dates with daily recurrence."""
        start_date = datetime(2024, 1, 1, 10, 0, tzinfo=pytz.UTC)
        end_date = date(2024, 2, 2)
        recurrence = 'Monthly'
        dates = calculate_lesson_dates(start_date, end_date, recurrence)
        self.assertEqual(dates, [
            datetime(2024, 1, 1, 10, 0, tzinfo=pytz.UTC),
            datetime(2024, 1, 31, 10, 0, tzinfo=pytz.UTC),
        ])

    def test_calculate_lesson_dates_invalid_recurrence(self):
        """Test calculate_lesson_dates with invalid recurrence."""
        start_date = datetime(2024, 1, 1, 10, 0, tzinfo=pytz.UTC)
        end_date = date(2024, 1, 3)
        recurrence = 'Invalid'
        dates = calculate_lesson_dates(start_date, end_date, recurrence)
        self.assertEqual(dates, [])

    def test_days_between(self):
        """Test days_between function."""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 10)
        self.assertEqual(days_between(start_date, end_date), 9)

    def test_calculate_invoice_amount_no_lesson(self):
        """Test calculate_invoice_amount with no recurrence."""
        lesson = None
        amount = calculate_invoice_amount(lesson)
        self.assertGreaterEqual(amount, 10.0)  # Random value between 10 and 200
        self.assertLessEqual(amount, 200.0)

    def test_calculate_invoice_amount_no_recurrence(self):
        """Test calculate_invoice_amount with no recurrence."""
        lesson = Lesson(date=datetime(2024, 1, 1, 10, 0, tzinfo=pytz.UTC), duration=60, recurrence='None')
        amount = calculate_invoice_amount(lesson)
        self.assertEqual(amount, 30.0)  # 60 * 0.5 * 1

    def test_calculate_invoice_amount_daily_recurrence(self):
        """Test calculate_invoice_amount with daily recurrence."""
        lesson = Lesson.objects.create(
            student=User.objects.get(pk=1),
            subject=Subject.objects.get(pk=1),
            date=datetime(2024, 1, 1, 10, 0, tzinfo=pytz.UTC),
            duration=60,
            recurrence='Daily',
            recurrence_end_date=date(2024, 1, 4),
        )
        amount = calculate_invoice_amount(lesson)
        self.assertEqual(amount, 90.0)  # 60 * 0.5 * 3 days

    def test_calculate_invoice_amount_weekly_recurrence(self):
        """Test calculate_invoice_amount with daily recurrence."""
        lesson = Lesson.objects.create(
            student=User.objects.get(pk=1),
            subject=Subject.objects.get(pk=1),
            date=datetime(2024, 1, 1, 10, 0, tzinfo=pytz.UTC),
            duration=60,
            recurrence='Weekly',
            recurrence_end_date=date(2024, 1, 18),
        )
        amount = calculate_invoice_amount(lesson)
        self.assertEqual(amount, 60)  # 60 * 0.5 * 2 weeks

    def test_calculate_invoice_amount_monthly_recurrence(self):
        """Test calculate_invoice_amount with daily recurrence."""
        lesson = Lesson.objects.create(
            student=User.objects.get(pk=1),
            subject=Subject.objects.get(pk=1),
            date=datetime(2024, 1, 1, 10, 0, tzinfo=pytz.UTC),
            duration=60,
            recurrence='Monthly',
            recurrence_end_date=date(2024, 3, 2),
        )
        amount = calculate_invoice_amount(lesson)
        self.assertEqual(amount, 60)  # 60 * 0.5 * 2 months

    def test_model_is_valid_valid_model(self):
        """Test model_is_valid with a valid model."""
        self.assertTrue(model_is_valid('User'))
        self.assertTrue(model_is_valid('Lesson'))

    def test_model_is_valid_invalid_model(self):
        """Test model_is_valid with an invalid model."""
        self.assertFalse(model_is_valid('InvalidModel'))

    def test_login_prohibited_anonymous_user(self):
        """Test login_prohibited decorator with an anonymous user."""
        @login_prohibited
        def dummy_view(request):
            return "Allowed"

        request = HttpRequest()
        request.user = AnonymousUser()
        response = dummy_view(request)
        self.assertEqual(response, "Allowed")

    def test_login_prohibited_authenticated_student(self):
        """Test login_prohibited decorator with an authenticated student user."""
        @login_prohibited
        def dummy_view(request):
            return "Allowed"

        student_user = User.objects.get(pk=1)
        self.client.login(username=student_user.username, password='Password123')
        request = HttpRequest()
        request.user = student_user
        response = dummy_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/student/dashboard/', response.url)

    def test_login_prohibited_authenticated_tutor(self):
        """Test login_prohibited decorator with an authenticated student user."""
        @login_prohibited
        def dummy_view(request):
            return "Allowed"

        tutor_user = User.objects.get(pk=2)
        self.client.login(username=tutor_user.username, password='Password123')
        request = HttpRequest()
        request.user = tutor_user
        response = dummy_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/tutor/dashboard/', response.url)

    def test_login_prohibited_authenticated_admin(self):
        """Test login_prohibited decorator with an authenticated student user."""
        @login_prohibited
        def dummy_view(request):
            return "Allowed"

        admin_user = User.objects.get(pk=3)
        self.client.login(username=admin_user.username, password='Password123')
        request = HttpRequest()
        request.user = admin_user
        response = dummy_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/dashboard/', response.url)
