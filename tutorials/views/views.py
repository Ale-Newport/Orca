from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from tutorials.forms import LogInForm, PasswordForm, UserForm, SignUpForm
from tutorials.helpers import login_prohibited
from django.utils import timezone
from tutorials.models import Lesson, Invoice
from ..forms import LessonRequestForm
from calendar import monthrange
from datetime import datetime, timedelta
from decimal import Decimal
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from datetime import datetime


@login_required
def dashboard(request):
    user = request.user
    upcoming_lessons = Lesson.objects.filter(student=user, date__gte=timezone.now()).order_by('date')[:5]
    unpaid_invoices = Invoice.objects.filter(student=user, paid=False)
    context = {
        'user': user,
        'upcoming_lessons': upcoming_lessons,
        'unpaid_invoices': unpaid_invoices,
    }
    return render(request, 'dashboard.html', context)


@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'home.html')


@login_required
def view_schedule(request, year=None, month=None):
    user = request.user
    # Use current year and month if not provided
    today = datetime.today()
    year = year or today.year
    month = month or today.month

    # Get lessons for the given month
    lessons = Lesson.objects.filter(
        student=user,
        date__year=year,
        date__month=month
    )

    # Generate calendar structure
    days_in_month = monthrange(year, month)[1]
    calendar = [
        {
            "day": day,
            "lessons": [
                lesson for lesson in lessons if lesson.date.day == day
            ]
        }
        for day in range(1, days_in_month + 1)
    ]

    # Context data
    context = {
        "calendar": calendar,
        "month": month,
        "year": year,
        "prev_month": (month - 1) if month > 1 else 12,
        "prev_year": year if month > 1 else year - 1,
        "next_month": (month + 1) if month < 12 else 1,
        "next_year": year if month < 12 else year + 1,
    }
    return render(request, 'view_schedule.html', context)

@login_required
def invoices(request):
    user_invoices = Invoice.objects.filter(student=request.user).order_by('-issued_date')
    return render(request, 'invoices.html', {'invoices': user_invoices})


class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in."""

    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        """Redirect when logged in, or dispatch as normal otherwise."""
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)

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


class LogInView(LoginProhibitedMixin, View):
    """Display login screen and handle user login."""

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def get(self, request):
        """Display log in template."""

        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handle log in attempt."""

        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
        user = form.get_user()
        if user is not None:
            login(request, user)
            if user.username == "@administrator":
                return redirect('requests')
            return redirect(self.next)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
        return self.render()

    def render(self):
        """Render log in template with blank log in form."""

        form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': self.next})


def log_out(request):
    """Log out the current user"""

    logout(request)
    return redirect('home')


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
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect the user after successful password change."""

        messages.add_message(self.request, messages.SUCCESS, "Password updated!")
        return reverse('dashboard')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Display user profile editing screen, and handle profile modifications."""

    model = UserForm
    template_name = "profile.html"
    form_class = UserForm

    def get_object(self):
        """Return the object (user) to be updated."""
        user = self.request.user
        return user

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)


class SignUpView(LoginProhibitedMixin, FormView):
    """Display the sign up screen and handle sign ups."""

    form_class = SignUpForm
    template_name = "sign_up.html"
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)
    
# Custom decorator to check if the user has the username "administrator"
def specific_user_only(user):
    return user.username == "@administrator"

# View for the specific user page
@user_passes_test(specific_user_only, login_url='/log_in/')  # Redirect others to login
def requestsView(request):
    return render(request, 'lesson_requests.html')

# check user type while login in to different dashboard
@login_required
def student_dashboard(request):
    if not request.user.is_student():
        return redirect('tutor_dashboard')  # Restrict to students
    return render(request, 'dashboard.html')

@login_required
def tutor_dashboard(request):
    if not request.user.is_tutor():
        return redirect('student_dashboard')  # Restrict to tutors
    return render(request, 'tutor_dashboard.html')


@login_required
def request_lesson(request):
    if request.method == 'POST':
        form = LessonRequestForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.status = 'Pending'
            lesson.student = request.user
            lesson.date = form.cleaned_data['date']
            lesson.save()
            # Generate Invoice if needed
            # generate_invoice_for_lesson(lesson)
            messages.success(request, 'Your lesson request has been submitted and is currently pending approval.')
            return redirect('view_upcoming_lessons')
        else:
            messages.error(request, 'There was an error with your submission. Please check the form for details.')
    else:
        form = LessonRequestForm()
    return render(request, 'request_lesson.html', {'form': form})
    
