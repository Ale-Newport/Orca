from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.timezone import now
from datetime import timedelta
from decimal import Decimal


class User(AbstractUser):
    """Model used for user authentication, and team member related information."""
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('tutor', 'Tutor'),
        ('student', 'Student'),
    )

    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^@\w{3,}$',
            message='Username must consist of @ followed by at least three alphanumericals'
        )]
    )
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)
    type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')

    class Meta:
        """Model options."""
        ordering = ['last_name', 'first_name']

    def full_name(self):
        """Return a string containing the user's full name."""
        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        return self.gravatar(size=60)


class Lesson(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lessons")
    subject = models.CharField(max_length=100, choices=[
        ('Python', 'Python'),
        ('Java', 'Java'),
        ('C++', 'C++'),
        ('Scala', 'Scala'),
        ('Web Development', 'Web Development'),
    ])
    date = models.DateTimeField()
    duration = models.PositiveIntegerField(validators=[MinValueValidator(30), MaxValueValidator(120)])
    tutor = models.CharField(max_length=100, default="Unknown Tutor")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    notes = models.TextField(blank=True, null=True)

    def is_assigned(self):
        """Return True if a tutor has been assigned."""
        return self.tutor != "Unknown Tutor"

    is_assigned.boolean = True  # Show as a boolean field in the admin interface
    is_assigned.short_description = 'Assigned?'

    def __str__(self):
        return f"{self.subject} with {self.student.username} on {self.date}"
    
    
class Invoice(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invoices')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    issued_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    paid = models.BooleanField(default=False)
    def __str__(self):
        status = "Paid" if self.paid else "Unpaid"
        return f"Invoice {self.id} for {self.student} - {status}"
