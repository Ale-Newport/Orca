from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .lessons_models import Lesson

User = get_user_model()

class Invoice(models.Model):
    student = models.ForeignKey('user_models.StudentUser', on_delete=models.CASCADE, related_name='invoices')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, related_name='invoices')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    issued_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    paid = models.BooleanField(default=False)

    def clean(self):
        """Ensure that the due date is after the issued date."""
        if self.due_date <= self.issued_date:
            raise ValidationError('Due date must be after the issued date.')
        if self.amount < 0:
            raise ValidationError('Amount must be greater or equal to zero.')
        if self.lesson and self.student != self.lesson.student:
            raise ValidationError('Student must match the lesson student.')

    def __str__(self):
        return f"Invoice {self.id} for {self.student} - {'Paid' if self.paid else 'Unpaid'}"

class Notification(models.Model):
    """Model to store notifications for users."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username} - {'Read' if self.is_read else 'Unread'}"
