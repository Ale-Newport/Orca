from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from libgravatar import Gravatar
from django.conf import settings
from tutorials.helpers import calculate_lesson_dates
from django.utils import timezone


class Subject(models.Model):
    """Model to represent a subject."""
    SUBJECT_CHOICES = [
        ('Python', 'Python'),
        ('Java', 'Java'),
        ('C++', 'C++'),
        ('Scala', 'Scala'),
        ('Web Development', 'Web Development'),
    ]
    name = models.CharField(max_length=50, choices=SUBJECT_CHOICES, unique=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    """Model used for user authentication, and team member related information."""
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('tutor', 'Tutor'),
        ('student', 'Student'),
    )

    username = models.CharField(max_length=30, unique=True,
        validators=[RegexValidator(
            regex=r'^@\w{3,}$',
            message='Username must consist of @ followed by at least three alphanumericals'
        )]
    )
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)
    type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    subjects = models.ManyToManyField(Subject, blank=True, related_name='tutors')

    class Meta:
        """Model options."""
        ordering = ['last_name', 'first_name']
    
    def clean(self):
        super().clean()
        """Ensure that the admin user has staff and superuser permissions."""
        if self.type == 'admin':
            self.is_staff = True
            self.is_superuser = True

    def full_name(self):
        """Return a string containing the user's full name."""
        return f'{self.first_name} {self.last_name}'

    def get_subjects(self):
        return ", ".join([subject.name for subject in self.subjects.all()])

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        return self.gravatar(size=60)
        
    def __str__(self):
        return self.username[1:] if self.username.startswith('@') else self.username


class Lesson(models.Model):
    """Model for lessons for a student given by a tutor on a subject."""
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    RECURRENCE_CHOICES = [
        ('None', 'None'),
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
    ]

    student = models.ForeignKey(User, limit_choices_to={'type': 'student'}, on_delete=models.CASCADE, related_name="lessons", blank=False)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, blank=False)
    tutor = models.ForeignKey(User, limit_choices_to={'type': 'tutor'}, on_delete=models.SET_DEFAULT, default=None, null=True)
    date = models.DateTimeField()
    duration = models.PositiveIntegerField(validators=[MinValueValidator(30), MaxValueValidator(240), RegexValidator(regex=r'^[1-9][0-9]*[05]$|^[1-9][0-9]*0$', message='Duration must be in 15 minute increments.')])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    recurrence = models.CharField(max_length=10, choices=RECURRENCE_CHOICES, default='None')
    recurrence_end_date = models.DateField(blank=True, null=True, default=None)

    def is_assigned(self):
        """Return True if a tutor has been assigned."""
        return self.tutor is not None
    is_assigned.boolean = True
    is_assigned.short_description = 'Assigned?'

    def lesson_dates(self):
        """Return a list of all lesson dates."""
        return calculate_lesson_dates(self.date, self.recurrence_end_date, self.recurrence)
    lesson_dates.short_description = 'Lesson Dates'

    def is_upcoming(self):
        """Return True if the lesson is upcoming."""
        return self.next_lesson() != None
    is_upcoming.boolean = True
    is_upcoming.short_description = 'Upcoming?'

    def next_lesson(self):
        """Return the next lesson date."""
        for date in self.lesson_dates():
            if date > timezone.now():
                return date
        return None
    next_lesson.short_description = 'Next Lesson'

    def paid(self):
        """Return True if the lesson has been paid for."""
        return Invoice.objects.filter(lesson=self, paid=True).exists()
    is_assigned.boolean = True
    is_assigned.short_description = 'Paid?'

    def has_invoice(self):
        """Return True if the lesson has been has an invoice."""
        return Invoice.objects.filter(lesson=self).exists()
    is_assigned.boolean = True
    is_assigned.short_description = 'Invoice?'

    def clean(self):
        """Ensure that the lesson date and recurrence end date are valid."""
        if self.recurrence != 'None' and not self.recurrence_end_date:
            raise ValidationError('Recurrence end date must be set for recurring lessons.')
        if self.recurrence_end_date and self.recurrence == 'None':
            raise ValidationError('Recurrence must be set to have a recurrence end date.')
        if self.recurrence_end_date and self.date and self.recurrence_end_date < self.date.date():
            raise ValidationError('Recurrence end date must be after the lesson date.')

    def __str__(self):
        return f"{self.subject} with {self.student} on {self.date.strftime('%d/%m/%Y %H:%M')}"


class Invoice(models.Model):
    student = models.ForeignKey(User, limit_choices_to={'type': 'student'}, on_delete=models.CASCADE, related_name='invoices')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, related_name='invoices', default=None)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    due_date = models.DateField()
    paid = models.BooleanField(default=False)

    def is_overdue(self):
        """Return True if the invoice is overdue."""
        return not self.paid and self.due_date < timezone.now().date()

    def clean(self):
        """Ensure that the student matches the lesson student."""
        if self.lesson and self.student != self.lesson.student:
            raise ValidationError('Student must match the lesson student.')

    def __str__(self):
        return f"Invoice {self.id} for {self.student} - {'Paid' if self.paid else 'Unpaid'}"


class Notification(models.Model):
    """Model to store notifications for users."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username} - {'Read' if self.is_read else 'Unread'}"
