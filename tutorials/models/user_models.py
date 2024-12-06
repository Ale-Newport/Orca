from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from libgravatar import Gravatar
from .subject_models import Subject

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

    class Meta:
        """Model options."""
        ordering = ['last_name', 'first_name']
        abstract = True

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
    
    def __str__(self):
        return self.username

class AdminUser(User):
    """Model for admin users."""
    role = models.CharField(max_length=50, blank=False)

class TutorUser(User):
    """Model for tutor users."""
    subjects = models.ManyToManyField(Subject, blank=False)
    enrollment_date = models.DateField(auto_now_add=True)

class StudentUser(User):
    """Model for student users."""
    enrollment_date = models.DateField(auto_now_add=True)
    grade_level = models.IntegerField(blank=True)