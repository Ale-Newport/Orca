from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from libgravatar import Gravatar
from django.conf import settings


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
    
    def clean(self):
        if self.type == 'tutor' and self.subjects.count() == 0:
            raise ValidationError('Tutors must teach at least one subject.')
        if not self.type == 'tutor' and not self.subjects.count() == 0:
            raise ValidationError('Only tutors can have subject.')
        
    def __str__(self):
        return self.username


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

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lessons")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, blank=False)
    tutor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField()
    duration = models.PositiveIntegerField(validators=[MinValueValidator(30), MaxValueValidator(240)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    recurrence = models.CharField(max_length=10, choices=RECURRENCE_CHOICES, default='None')
    recurrence_end_date = models.DateField(blank=True, null=True)

    def is_assigned(self):
        """Return True if a tutor has been assigned."""
        return self.tutor is not None

    is_assigned.boolean = True
    is_assigned.short_description = 'Assigned?'

    def clean(self):
        """Ensure that the lesson date and recurrence end date are valid."""
        if self.recurrence != 'None' and not self.recurrence_end_date:
            raise ValidationError('Recurrence end date must be set for recurring lessons.')
        if self.recurrence_end_date and self.recurrence == 'None':
            raise ValidationError('Recurrence must be set to have a recurrence end date.')
        if self.recurrence_end_date and self.recurrence_end_date < self.date.date():
            raise ValidationError('Recurrence end date must be after the lesson date.')
        """Ensure that the duration is valid."""
        if self.duration % 15 != 0:
            raise ValidationError('Duration must be in 15 minute increments.')
        if self.duration < 30 or self.duration > 240:
            raise ValidationError('Duration must be between 30 and 240 minutes.')
        """Ensure that the student is a student and the tutor is a tutor."""
        if self.student.type != 'student':
            raise ValidationError('The student must be a user of type student.')
        if self.tutor and self.tutor.type != 'tutor':
            raise ValidationError('The tutor must be a user of type tutor.')

    def __str__(self):
        return f"{self.subject} with {self.student} on {self.date}"



class Invoice(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invoices')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, related_name='invoices')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    paid = models.BooleanField(default=False)

    def clean(self):
        """Ensure that the amount is greater than or equal to zero."""
        if self.amount < 0:
            raise ValidationError('Amount must be greater or equal to zero.')
        """Ensure that the student matches the lesson student."""
        if self.student.type != 'student':
            raise ValidationError('The student must be a user of type student.')
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
