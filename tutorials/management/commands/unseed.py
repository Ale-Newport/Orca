from django.core.management.base import BaseCommand, CommandError
from tutorials.models import User, Subject, Lesson, Invoice, Notification

class Command(BaseCommand):
    """Build automation command to unseed the database."""
    
    help = 'Seeds the database with sample data'

    def handle(self, *args, **options):
        """Unseed the database."""

        User.objects.all().delete()
        Lesson.objects.all().delete()
        Subject.objects.all().delete()
        Invoice.objects.all().delete()
        Notification.objects.all().delete()