from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from tutorials.views import LoginProhibitedMixin
from django.shortcuts import redirect
from django.urls import reverse

class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in."""

    def dispatch(self, *args, **kwargs):
        """Redirect when logged in, or dispatch as normal otherwise."""
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        """Handle when user is already logged in."""
        user = self.request.user
        if user.type == 'admin':
            return redirect('admin_dashboard')
        elif user.type == 'tutor':
            return redirect('tutor_dashboard')
        else:
            return redirect('student_dashboard')