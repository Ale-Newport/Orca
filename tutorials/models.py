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
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lessons"
    )
    subject = models.CharField(max_length=100)
    date = models.DateTimeField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    tutor = models.CharField(max_length=100, default="Unknown Tutor")

    def __str__(self):
        return f"{self.subject} with {self.student.username} on {self.date}"

    def save(self, *args, **kwargs):
        """Override the save method to create an invoice when a lesson is added."""
        creating = self.pk is None  # Check if this is a new lesson
        super().save(*args, **kwargs)

        if creating:  # If it's a new lesson, create an invoice
            amount = Decimal(self.duration * 10)  # Example: $10 per minute
            due_date = self.date.date() + timedelta(days=7)  # Due in 7 days
            Invoice.objects.create(
                student=self.student,
                amount=amount,
                due_date=due_date
            )

class Invoice(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invoices')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    issued_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    paid = models.BooleanField(default=False)

    def __str__(self):
        status = "Paid" if self.paid else "Unpaid"
        return f"Invoice {self.id} for {self.student} - {status}"


