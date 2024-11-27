from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .models import User, Lesson
from datetime import datetime, timedelta

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


class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        """Form options."""
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']


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

    USER_TYPE_CHOICES = (
        ('tutor', 'Tutor'),
        ('student', 'Student'),
    )

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


class LessonRequestForm(forms.ModelForm):
    preferred_date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type':'datetime-local', 'step': 900}), required=True) # 900 seconds = 15 minutes
    duration = forms.IntegerField(widget=forms.NumberInput(attrs={'type': 'number', 'step': 15, 'min': 30, 'max': 240}), required=True)
    recurrence = forms.ChoiceField(choices=[('None', 'None'), ('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly')], required=False)
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False)

    class Meta:
        model = Lesson
        fields = ['subject', 'preferred_date', 'duration', 'recurrence', 'end_date', 'notes']

    def clean(self):
        cleaned_data = super().clean()
        preferred_date = cleaned_data.get('preferred_date')
        duration = cleaned_data.get('duration')
        recurrence = cleaned_data.get('recurrence')
        end_date = cleaned_data.get('end_date')

        # Check if the time is in 15-minute intervals
        if duration % 15 != 0:
            raise forms.ValidationError('Please select a duration in 15-minute intervals.')

        # Check if the duration is at least 30 minutes
        if duration < 30:
            raise forms.ValidationError('The duration must be at least 30 minutes.')

        # Check if end_date is provided when recurrence is not 'None'
        if recurrence != 'None' and not end_date:
            raise forms.ValidationError('Please enter an end date for the recurrence.')

        # Check if end_date is provided without a recurrence
        if end_date and recurrence == 'None':
            raise forms.ValidationError('To have an end date, you must select a recurrence.')

        return cleaned_data
