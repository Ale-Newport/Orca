from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from tutorials.forms import LogInForm, PasswordForm, SignUpForm, UserForm, UserFormAdmin, UserFormTutor
from tutorials.helpers import login_prohibited

@login_prohibited
def home(request):
    """Display the application's home screen."""
    return render(request, 'home.html')

class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in."""

    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        """Redirect when logged in, or dispatch as normal otherwise."""
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        user = self.request.user
        if user.type == 'admin':
            return redirect('admin:index')
        elif user.type == 'tutor':
            return redirect('tutor_dashboard')
        else:
            return redirect('dashboard')

    def get_redirect_when_logged_in_url(self):
        """Returns the url to redirect to when not logged in."""
        if self.redirect_when_logged_in_url is None:
            raise ImproperlyConfigured(
                "LoginProhibitedMixin requires either a value for "
                "'redirect_when_logged_in_url', or an implementation for "
                "'get_redirect_when_logged_in_url()'."
            )
        else:
            return self.redirect_when_logged_in_url

class PasswordView(LoginRequiredMixin, FormView):
    """Display password change screen and handle password change requests."""

    template_name = 'password.html'
    form_class = PasswordForm

    def get_form_kwargs(self, **kwargs):
        """Pass the current user to the password change form."""
        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """Handle valid form by saving the new password."""
        form.save()
        login(self.request, self.request.user)
        messages.add_message(self.request, messages.SUCCESS, "Password updated!")
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect the user after successful password change."""
        user = self.request.user
        if user.type == 'admin':
            return reverse('admin_dashboard')
        elif user.type == 'tutor':
            return reverse('tutor_dashboard')
        else:
            return reverse('student_dashboard')

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Display user profile editing screen, and handle profile modifications."""

    template_name = "profile.html"

    def get_form_class(self):
        """Return the form class based on the user type."""
        user = self.request.user
        if user.type == 'tutor':
            return UserFormTutor
        else:
            return UserForm

    def get_object(self):
        """Return the object (user) to be updated."""
        return self.request.user

    def get_success_url(self):
        """Return redirect URL after successful update."""
        user = self.request.user
        if user.type == 'admin':
            return reverse('admin_dashboard')
        elif user.type == 'tutor':
            return reverse('tutor_dashboard')
        else:
            return reverse('student_dashboard')

class SignUpView(LoginProhibitedMixin, FormView):
    """Display the sign up screen and handle sign ups."""

    form_class = SignUpForm
    template_name = "sign_up.html"

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return super().form_valid(form)

    def get_success_url(self):
        """Return the redirect URL based on user type."""
        user = self.object
        if user.type == 'admin':
            return reverse('admin_dashboard')
        elif user.type == 'tutor':
            return reverse('tutor_dashboard')
        else:
            return reverse('student_dashboard')

class LogInView(LoginProhibitedMixin, View):
    """Display login screen and handle user login."""
    http_method_names = ['get', 'post']

    def get(self, request):
        """Display log in template."""
        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handle log in attempt."""
        form = LogInForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            if user is not None:
                login(request, user)
                return redirect(self.get_redirect_url(user))
            else:
                messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
        else:
            messages.add_message(request, messages.ERROR, "Please correct the errors below.")
        return self.render()

    def render(self):
        """Render log in template with blank log in form."""
        form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': self.next})

    def get_redirect_url(self, user):
        """Return the redirect URL based on user type."""
        if user.type == 'admin':
            return reverse('admin_dashboard')
        elif user.type == 'tutor':
            return reverse('tutor_dashboard')
        else:
            return reverse('student_dashboard')


def log_out(request):
    """Log out the current user"""
    logout(request)
    return redirect('home')
