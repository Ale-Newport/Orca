from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from tutorials.models import User, Subject, Lesson, Invoice, Notification
from datetime import datetime, time, timedelta
from tutorials.helpers import calculate_lesson_dates

# Profile forms
class LogInForm(forms.Form):
    """Form enabling registered users to log in."""
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def get_user(self):
        """Returns authenticated user if possible."""
        user = None
        if self.is_valid():
            username = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
        return user

class NewPasswordMixin(forms.Form):
    """Form mixing for new_password and password_confirmation fields."""
    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
        )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Validate password confirmation."""
        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')

class PasswordForm(NewPasswordMixin, forms.Form):
    """Form enabling users to change their password."""
    password = forms.CharField(label='Current password', widget=forms.PasswordInput())

    def __init__(self, user=None, **kwargs):
        """Construct new form instance with a user instance."""
        super().__init__(**kwargs)
        self.user = user

    def clean(self):
        """Clean the data and generate messages for any errors."""
        super().clean()
        password = self.cleaned_data.get('password')
        new_password = self.cleaned_data.get('new_password')

        if new_password and len(new_password) < 8:
            self.add_error('new_password', "Password must be at least 8 characters long")
            
        if self.user is None:
            self.add_error('user', "User must be provided")
        if self.user is not None:
            user = authenticate(username=self.user.username, password=password)
        else:
            user = None
        if user is None:
            self.add_error('password', "Password is invalid")

    def save(self):
        """Save the user's new password."""
        new_password = self.cleaned_data['new_password']
        if self.user is not None:
            self.user.set_password(new_password)
            self.user.save()
        return self.user

class SignUpForm(NewPasswordMixin, forms.ModelForm):
    """Form enabling unregistered users to sign up."""
    USER_TYPE_CHOICES = (('student', 'Student'), ('tutor', 'Tutor'))
    type = forms.ChoiceField(choices=USER_TYPE_CHOICES, required=True)

    class Meta:
        """Form options."""
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'type']

    def clean(self):
        """Clean the data and generate messages for any errors."""
        super().clean()
        if not self.errors:  # Only check for duplicates if no other errors exist
            if User.objects.filter(email=self.cleaned_data.get('email')).exists():
                self.add_error('email', 'Email is already taken')
            if User.objects.filter(username=self.cleaned_data.get('username')).exists():
                self.add_error('username', 'Username is already taken')

    def save(self, commit=True):
        """Create a new user."""
        user = super().save(commit=False)
        user.type = self.cleaned_data.get('type')
        user.set_password(self.cleaned_data.get('new_password'))
        if commit:
            user.save()
        return user


# Lessons forms
class LessonForm(forms.ModelForm):
    student = forms.ModelChoiceField(queryset=User.objects.filter(type='student').order_by('username'), required=True)
    tutor = forms.ModelChoiceField(queryset=User.objects.filter(type='tutor').order_by('username'), required=False)
    subject = forms.ModelChoiceField(queryset=Subject.objects.all().order_by('name'), required=True)
    duration = forms.IntegerField(widget=forms.NumberInput(attrs={'type': 'number', 'step': 15, 'min': 30, 'max': 240}), required=True)

    class Meta:
        model = Lesson
        fields = ['student', 'tutor', 'subject', 'date', 'duration', 'status', 'recurrence', 'recurrence_end_date']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'recurrence_end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        tutor = cleaned_data.get('tutor')
        subject = cleaned_data.get('subject')
        date = cleaned_data.get('date')
        duration = cleaned_data.get('duration')
        recurrence = cleaned_data.get('recurrence')
        recurrence_end_date = cleaned_data.get('recurrence_end_date')
        lesson_dates = calculate_lesson_dates(date, recurrence_end_date, recurrence)

        """Ensure that the lesson date and recurrence end date are valid."""
        if recurrence != 'None' and not recurrence_end_date:
            self.add_error('recurrence_end_date', 'Please enter an end date for the recurrence.')
        if recurrence_end_date is not None and recurrence == 'None':
            self.add_error('recurrence', 'To have an end date you must select a recurrence type.')
        if date.replace(tzinfo=None) < datetime.now():
            self.add_error('date', 'The date must be in the future.')
        if recurrence_end_date is not None and recurrence_end_date < date.date():
            self.add_error('recurrence_end_date', 'Please select an ending date that is after the preferred date.')
        """Ensure the tutor teaches the subject."""
        if tutor is not None and subject not in tutor.subjects.all():
            self.add_error('tutor', f'This tutor does not teach {subject}, it only teaches {tutor.get_subjects()}.')
            self.add_error('subject', f'The tutor {tutor} does not teach this subject.')
        """Ensure that the lesson date do not overlap."""
        for lesson_date in lesson_dates:
            lesson_end_time = lesson_date + timedelta(minutes=duration)
            overlapping_student_lessons = Lesson.objects.filter(student=student, date__lt=lesson_end_time, date__gte=date).exclude(pk=self.instance.pk)
            if overlapping_student_lessons.exists():
                overlapping_details = ', '.join([f"{ol.subject} on {ol.date.strftime('%d/%m/%Y %H:%M')}" for ol in overlapping_student_lessons])
                self.add_error('date', f'The lesson time overlaps for the student {student} with an existing lesson: {overlapping_details}')
                break
            if tutor is not None:
                overlapping_tutor_lessons = Lesson.objects.filter(tutor=tutor, date__lt=lesson_end_time, date__gte=date).exclude(pk=self.instance.pk)
                if overlapping_tutor_lessons.exists():
                    overlapping_details = ', '.join([f"{ol.subject} on {ol.date.strftime('%d/%m/%Y %H:%M')}" for ol in overlapping_tutor_lessons])
                    self.add_error('date', f'The lesson time overlaps for the tutor {tutor} with an existing lesson: {overlapping_details}')
                    self.add_error('tutor', f'The tutor {tutor} has an overlapping lesson on {lesson_date.strftime("%d/%m/%Y %H:%M")}, choose other tutor or change date.')
                    break
        
        return cleaned_data

class RequestForm(forms.ModelForm):
    date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type':'datetime-local'}))
    duration = forms.IntegerField(widget=forms.NumberInput(attrs={'type': 'number', 'step': 15, 'min': 30, 'max': 240}))

    class Meta:
        model = Lesson
        fields = ['subject', 'date', 'duration', 'recurrence', 'recurrence_end_date']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'recurrence_end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        duration = cleaned_data.get('duration')
        recurrence = cleaned_data.get('recurrence')
        recurrence_end_date = cleaned_data.get('recurrence_end_date')
        lesson_dates = calculate_lesson_dates(date, recurrence_end_date, recurrence)

        """Ensure that the lesson date and recurrence end date are valid."""
        if recurrence != 'None' and not recurrence_end_date:
            self.add_error('recurrence_end_date', 'Please enter an end date for the recurrence.')
        if recurrence_end_date is not None and recurrence == 'None':
            self.add_error('recurrence', 'To have an end date you must select a recurrence type.')
        if date.replace(tzinfo=None) < datetime.now():
            self.add_error('date', 'The date must be in the future.')
        if recurrence_end_date is not None and recurrence_end_date < date.date():
            self.add_error('recurrence_end_date', 'Please select an ending date that is after the preferred date.')
        """Ensure that the duration is valid."""
        if duration % 15 != 0:
            self.add_error('duration', 'The duration must be in 15-minute intervals.')
        if duration < 30 or duration > 240:
            self.add_error('duration', 'The duration must be at least 30 minutes and no more than 240 minutes.')
        """Ensure date is within working hours (e.g., 8 AM to 8 PM)"""
        start_time = time(8, 0)  # 8:00 AM
        end_time = time(20, 0)   # 8:00 PM
        lesson_end_time = (date + timedelta(minutes=duration)).time()
        if not (start_time <= date.time() <= end_time and start_time <= lesson_end_time <= end_time):
            self.add_error('date', 'The preferred date must be within working hours (8 AM to 8 PM).')

        return cleaned_data


# User form
class UserForm(forms.ModelForm):
    """Form to update or create user profiles."""

    class Meta:
        """Form options."""
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'type', 'subjects']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.type == 'tutor':
            self.fields['subjects'].disabled = False
        else:
            self.fields['subjects'].required = False
            self.fields['subjects'].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        """Ensure the username and email is unique."""
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            self.add_error('username', 'This username is already taken.')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            self.add_error('email', 'This email is already taken.')
        
        return cleaned_data

class ProfileForm(forms.ModelForm):
    """Form to update one's user profile."""

    class Meta:
        """Form options."""
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.type == 'tutor':
            self.fields['subjects'] = forms.ModelMultipleChoiceField(queryset=Subject.objects.all(), required=True)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        """Ensure the username and email is unique."""
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            self.add_error('username', 'This username is already taken.')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            self.add_error('email', 'This email is already taken.')

        return cleaned_data


# Invoice form
class InvoiceForm(forms.ModelForm):
    """Form to update user profiles."""
    student = forms.ModelChoiceField(queryset=User.objects.filter(type='student').order_by('username'))
    lesson = forms.ModelChoiceField(queryset=Lesson.objects.all().order_by('student'), required=False)
    amount = forms.DecimalField(widget=forms.NumberInput(attrs={'min': 0, 'step': 0.50, 'placeholder': '£'}), max_digits=10, decimal_places=2)
    due_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    paid = forms.ChoiceField(choices=[(True, 'Paid'), (False, 'Not Paid')], widget=forms.Select(attrs={'class': 'form-control'}), initial=False)

    class Meta:
        model = Invoice
        fields = ['student', 'lesson', 'amount', 'due_date', 'paid']

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        lesson = cleaned_data.get('lesson')

        """Ensure that the student is a student."""
        if student not in User.objects.filter(type='student'):
            self.add_error('student', 'The student must be a user of type student.')
        """Ensure that the student matches the lesson student."""
        if lesson and student != lesson.student:
            self.add_error('student', 'Student must match the lesson student.')

        return cleaned_data


# Notification form
class NotificationForm(forms.ModelForm):
    """Form to create notifications."""
    user = forms.ModelChoiceField(queryset=User.objects.all().order_by('username'), required=True)
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True)

    class Meta:
        model = Notification
        fields = ['user', 'message']

    def clean(self):
        cleaned_data = super().clean()
        message = cleaned_data.get('message')

        # Ensure the message is not empty
        if not message:
            self.add_error('message', 'The message cannot be empty.')

        return cleaned_data