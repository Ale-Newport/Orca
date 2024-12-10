from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from tutorials.models import User, Lesson, Invoice, Subject

class LessonModelTest(TestCase):
    """Tests for the Lesson model."""

    fixtures = ['tutorials/tests/fixtures/subjects.json', 'tutorials/tests/fixtures/users.json']

    def setUp(self):
        self.student = User.objects.get(pk=1)
        self.tutor = User.objects.get(pk=2)
        self.subject = Subject.objects.get(pk=1)
        self.date = timezone.now() + timedelta(days=1)
        self.duration = 60
        self.recurrence_end_date = self.date.date() + timedelta(days=30)

    def test_lesson_creation(self):
        """Test that a lesson can be successfully created."""
        lesson = Lesson.objects.create(
            student=self.student,
            subject=self.subject,
            tutor=self.tutor,
            date=self.date,
            duration=self.duration,
            status="Pending",
            recurrence="None",
        )
        self.assertTrue(lesson)
        self.assertEqual(lesson.student, self.student)
        self.assertEqual(lesson.subject, self.subject)
        self.assertEqual(lesson.tutor, self.tutor)
        self.assertEqual(lesson.date, self.date)
        self.assertEqual(lesson.duration, self.duration)
        self.assertEqual(lesson.status, "Pending")
        self.assertEqual(lesson.recurrence, "None")

    def test_is_assigned(self):
        """Test the is_assigned method."""
        lesson = Lesson.objects.create(
            student=self.student,
            subject=self.subject,
            tutor=self.tutor,
            date=self.date,
            duration=self.duration,
        )
        self.assertTrue(lesson.is_assigned())

        lesson.tutor = None
        lesson.save()
        self.assertFalse(lesson.is_assigned())

    def test_clean_recurrence_end_date_required(self):
        """Test that recurrence end date is required for recurring lessons."""
        lesson = Lesson(
            student=self.student,
            subject=self.subject,
            date=self.date,
            duration=self.duration,
            recurrence="Weekly",
        )
        with self.assertRaises(ValidationError):
            lesson.clean()

    def test_clean_no_recurrence_with_end_date(self):
        """Test that recurrence must be set if recurrence end date is provided."""
        lesson = Lesson(
            student=self.student,
            subject=self.subject,
            date=self.date,
            duration=self.duration,
            recurrence="None",
            recurrence_end_date=self.recurrence_end_date,
        )
        with self.assertRaises(ValidationError):
            lesson.clean()

    def test_clean_recurrence_end_date_after_start_date(self):
        """Test that recurrence end date must be after the start date."""
        lesson = Lesson(
            student=self.student,
            subject=self.subject,
            date=self.date,
            duration=self.duration,
            recurrence="Weekly",
            recurrence_end_date=self.date.date() - timedelta(days=1),
        )
        with self.assertRaises(ValidationError):
            lesson.clean()

    def test_next_lesson(self):
        """Test the next_lesson method."""
        lesson = Lesson.objects.create(
            student=self.student,
            subject=self.subject,
            date=self.date,
            duration=self.duration,
            recurrence="None",
        )
        self.assertEqual(lesson.next_lesson(), lesson.date)

    def test_is_upcoming(self):
        """Test the is_upcoming method."""
        lesson = Lesson.objects.create(
            student=self.student,
            subject=self.subject,
            date=self.date,
            duration=self.duration,
        )
        self.assertTrue(lesson.is_upcoming())

        past_lesson_date = timezone.now() - timedelta(days=1)
        lesson.date = past_lesson_date
        lesson.save()
        self.assertFalse(lesson.is_upcoming())

    def test_paid(self):
        """Test the paid method."""
        lesson = Lesson.objects.create(
            student=self.student,
            subject=self.subject,
            date=self.date,
            duration=self.duration,
        )
        self.assertFalse(lesson.paid())

        Invoice.objects.create(
            student=self.student,
            lesson=lesson,
            amount=100.00,
            due_date=timezone.now() + timedelta(days=30),
            paid=True,
        )
        self.assertTrue(lesson.paid())

    def test_has_invoice(self):
        """Test the has_invoice method."""
        lesson = Lesson.objects.create(
            student=self.student,
            subject=self.subject,
            date=self.date,
            duration=self.duration,
        )
        self.assertFalse(lesson.has_invoice())

        Invoice.objects.create(
            student=self.student,
            lesson=lesson,
            amount=100.00,
            due_date=timezone.now() + timedelta(days=30),
        )
        self.assertTrue(lesson.has_invoice())

    def test_duration_validation(self):
        """Test that duration is validated for 15-minute increments."""
        invalid_duration = 35
        lesson = Lesson(
            student=self.student,
            subject=self.subject,
            date=self.date,
            duration=invalid_duration,
        )
        with self.assertRaises(ValidationError):
            lesson.full_clean()

    def test_string_representation(self):
        """Test the string representation of a lesson."""
        lesson = Lesson.objects.create(
            student=self.student,
            subject=self.subject,
            date=self.date,
            duration=self.duration,
        )
        expected_str = f"{self.subject} with {self.student} on {self.date.strftime('%d/%m/%Y %H:%M')}"
        self.assertEqual(str(lesson), expected_str)

    def test_lesson_without_tutor(self):
        """Test creating a lesson without assigning a tutor."""
        lesson = Lesson.objects.create(
            student=self.student,
            subject=self.subject,
            tutor=None,
            date=self.date,
            duration=self.duration,
        )
        self.assertFalse(lesson.is_assigned())
        self.assertEqual(lesson.tutor, None)

    def test_lesson_status_default(self):
        """Test the default status of a lesson."""
        lesson = Lesson.objects.create(
            student=self.student,
            subject=self.subject,
            date=self.date,
            duration=self.duration,
        )
        self.assertEqual(lesson.status, 'Pending')

    def test_lesson_status_update(self):
        """Test updating the lesson status."""
        lesson = Lesson.objects.create(
            student=self.student,
            subject=self.subject,
            date=self.date,
            duration=self.duration,
        )
        lesson.status = 'Approved'
        lesson.save()
        self.assertEqual(lesson.status, 'Approved')

    def test_lesson_recurrence_weekly(self):
        """Test weekly recurrence lesson dates."""
        recurrence_end_date = self.date.date() + timedelta(weeks=4)
        lesson = Lesson.objects.create(
            student=self.student,
            subject=self.subject,
            date=self.date,
            duration=self.duration,
            recurrence='Weekly',
            recurrence_end_date=recurrence_end_date,
        )
        dates = lesson.lesson_dates()
        self.assertEqual(len(dates), 5)  # 4 weeks + initial lesson
        self.assertTrue(all(date >= self.date for date in dates))

    def test_lesson_recurrence_daily(self):
        """Test daily recurrence lesson dates."""
        recurrence_end_date = self.date.date() + timedelta(days=6)
        lesson = Lesson.objects.create(
            student=self.student,
            subject=self.subject,
            date=self.date,
            duration=self.duration,
            recurrence='Daily',
            recurrence_end_date=recurrence_end_date,
        )
        dates = lesson.lesson_dates()
        self.assertEqual(len(dates), 7)  # 6 days + initial lesson
        self.assertTrue(all(date >= self.date for date in dates))

    def test_lesson_recurrence_no_end_date(self):
        """Test that recurrence without an end date raises an error."""
        lesson = Lesson(
            student=self.student,
            subject=self.subject,
            date=self.date,
            duration=self.duration,
            recurrence='Weekly',
            recurrence_end_date=None,
        )
        with self.assertRaises(ValidationError):
            lesson.full_clean()

    def test_lesson_recurrence_none_with_end_date(self):
        """Test that setting an end date for no recurrence raises an error."""
        lesson = Lesson(
            student=self.student,
            subject=self.subject,
            date=self.date,
            duration=self.duration,
            recurrence='None',
            recurrence_end_date=self.date.date() + timedelta(weeks=4),
        )
        with self.assertRaises(ValidationError):
            lesson.full_clean()

    def test_lesson_recurrence_end_date_before_date(self):
        """Test that recurrence end date before the initial date raises an error."""
        lesson = Lesson(
            student=self.student,
            subject=self.subject,
            date=self.date,
            duration=self.duration,
            recurrence='Weekly',
            recurrence_end_date=self.date.date() - timedelta(days=1),
        )
        with self.assertRaises(ValidationError):
            lesson.full_clean()

    def test_lesson_paid_with_multiple_invoices(self):
        """Test the paid method when there are multiple invoices."""
        lesson = Lesson.objects.create(
            student=self.student,
            subject=self.subject,
            date=self.date,
            duration=self.duration,
        )
        Invoice.objects.create(
            student=self.student,
            lesson=lesson,
            amount=100.00,
            due_date=timezone.now() + timedelta(days=30),
            paid=False,
        )
        self.assertFalse(lesson.paid())

        Invoice.objects.create(
            student=self.student,
            lesson=lesson,
            amount=100.00,
            due_date=timezone.now() + timedelta(days=30),
            paid=True,
        )
        self.assertTrue(lesson.paid())

    def test_lesson_no_student(self):
        """Test that a lesson without a student raises an error."""
        lesson = Lesson(
            subject=self.subject,
            date=self.date,
            duration=self.duration,
        )
        with self.assertRaises(ValidationError):
            lesson.full_clean()

    def test_invalid_duration(self):
        """Test invalid durations that do not conform to 15-minute increments."""
        lesson = Lesson(
            student=self.student,
            subject=self.subject,
            date=self.date,
            duration=35,  # Invalid duration
        )
        with self.assertRaises(ValidationError):
            lesson.full_clean()

    def test_lessons_related_to_student(self):
        """Test that lessons are correctly related to a student."""
        lesson = Lesson.objects.create(
            student=self.student,
            subject=self.subject,
            date=self.date,
            duration=self.duration,
        )
        self.assertIn(lesson, self.student.lessons.all())
