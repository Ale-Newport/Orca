from django.db import models

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