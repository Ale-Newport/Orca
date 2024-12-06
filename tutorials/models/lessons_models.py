from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .subject_models import Subject

User = get_user_model()

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

    student = models.ForeignKey('user_models.StudentUser', on_delete=models.CASCADE, related_name="lessons")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, blank=False)
    tutor = models.ForeignKey('user_models.TutorUser', on_delete=models.SET_NULL, null=True)
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
        if self.duration % 15 != 0:
            raise ValidationError('Duration must be in 15 minute increments.')

    def __str__(self):
        return f"{self.subject} with {self.student} on {self.date}"

