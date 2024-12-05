from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from .models import User, Lesson, Invoice
from datetime import datetime, time, timedelta

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

class PasswordForm(NewPasswordMixin):
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
    USER_TYPE_CHOICES = (('tutor', 'Tutor'), ('student', 'Student'))
    type = forms.ChoiceField(choices=USER_TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}), initial='student')

    class Meta:
        """Form options."""
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'type']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        """Create a new user."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['new_password'])
        if commit:
            user.save()
        return user


# Lessons forms
class LessonRequestForm(forms.ModelForm):
    preferred_date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type':'datetime-local'}), required=True)
    duration = forms.IntegerField(widget=forms.NumberInput(attrs={'type': 'number', 'step': 15, 'min': 30, 'max': 240}), required=True)
    recurrence = forms.ChoiceField(choices=[('None', 'None'), ('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly')], required=False)
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta:
        model = Lesson
        fields = ['subject', 'preferred_date', 'duration', 'recurrence', 'end_date', 'notes']

    def clean(self):
        cleaned_data = super().clean()
        preferred_date = cleaned_data.get('preferred_date')
        duration = cleaned_data.get('duration')
        recurrence = cleaned_data.get('recurrence')
        end_date = cleaned_data.get('end_date')

        # Ensure duration is in 15-minute intervals
        if duration % 15 != 0:
            self.add_error('duration', 'Please select a duration in 15-minute intervals.')
        # Ensure duration is within a reasonable range
        if duration < 30 or duration > 240:
            self.add_error('duration', 'The duration must be at least 30 minutes and less than 240 minutes.')
        # Ensure end_date is provided when recurrence is not 'None'
        if recurrence != 'None' and not end_date:
            self.add_error('end_date', 'Please enter an end date for the recurrence.')
        # Ensure end_date is provided without a recurrence
        if end_date and recurrence == 'None':
            self.add_error('recurrence', 'To have an end date you must select a recurrence type.')
        # Ensure preferred_date is in the future
        if preferred_date.replace(tzinfo=None) < datetime.now():
            self.add_error('preferred_date', 'The date should be in the future.')
        # Ensure end_date is after preferred_date
        if end_date and end_date < preferred_date.date():
            self.add_error('end_date', 'Please select an ending date that is after the preferred date.')
        # Ensure preferred_date is within working hours (e.g., 8 AM to 8 PM)
        start_time = time(8, 0)  # 8:00 AM
        end_time = time(20, 0)   # 8:00 PM
        lesson_end_time = (preferred_date + timedelta(minutes=duration)).time()
        if not (start_time <= preferred_date.time() <= end_time and start_time <= lesson_end_time <= end_time):
            self.add_error('preferred_date', 'The preferred date must be within working hours (8 AM to 8 PM).')

        return cleaned_data

class LessonForm(forms.ModelForm):
    student = forms.ModelChoiceField(queryset=User.objects.filter(type='student').order_by('username'), required=True)
    tutor = forms.ModelChoiceField(queryset=User.objects.filter(type='tutor').order_by('username'), required=True)
    date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type':'datetime-local'}), required=True)
    duration = forms.IntegerField(widget=forms.NumberInput(attrs={'type': 'number', 'step': 15, 'min': 30, 'max': 240}), required=True)
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta:
        model = Lesson
        fields = ['student', 'subject', 'tutor', 'date', 'duration', 'notes']

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        duration = cleaned_data.get('duration')

        # Ensure duration is in 15-minute intervals
        if duration % 15 != 0:
            self.add_error('duration', 'The duration must be in 15-minute intervals.')
        # Ensure duration is within a reasonable range
        if duration < 30 or duration > 240:
            self.add_error('duration', 'The duration must be at least 30 minutes and less than 240 minutes.')
        # Ensure preferred_date is in the future
        if date.replace(tzinfo=None) < datetime.now():
            self.add_error('date', 'The date must be in the future.')
        # Ensure date is within working hours (e.g., 8 AM to 8 PM)
        start_time = time(8, 0)  # 8:00 AM
        end_time = time(20, 0)   # 8:00 PM
        lesson_end_time = (date + timedelta(minutes=duration)).time()
        if not (start_time <= date.time() <= end_time and start_time <= lesson_end_time <= end_time):
            self.add_error('date', 'The date must be within working hours (8 AM to 8 PM).')

        return cleaned_data

# User form
class UserForm(forms.ModelForm):
    """Form to update user profiles."""
    class Meta:
        """Form options."""
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'type']

# Invoice form
class InvoiceForm(forms.ModelForm):
    student = forms.ModelChoiceField(queryset=User.objects.filter(type='student').order_by('username'), required=True)
    amount = forms.DecimalField(widget=forms.NumberInput(attrs={'min': 0, 'step': 0.50, 'placeholder': '£'}), max_digits=10, decimal_places=2, required=True)
    due_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    paid = forms.ChoiceField(choices=[(True, 'Paid'), (False, 'Not Paid')], widget=forms.Select(attrs={'class': 'form-control'}), required=True, initial=False)

    class Meta:
        model = Invoice
        fields = ['student', 'amount', 'due_date', 'paid']

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        due_date = cleaned_data.get('due_date')

        # Ensure the amount is a positive value
        if amount is not None and amount <= 0:
            self.add_error('amount', 'The amount must be greater than 0.')

        # Ensure due_date is in the future
        if due_date and due_date < datetime.now().date():
            self.add_error('due_date', 'The due date must be in the future.')

        return cleaned_data
