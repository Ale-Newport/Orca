from django.shortcuts import redirect
from django.apps import apps
from datetime import datetime, timedelta
from random import randint
import pytz

def calculate_lesson_dates(start_date, end_date, recurrence):
        """Calculate all lesson dates based on recurrence and recurrence_end_date."""
        dates = []
        current_date = start_date
        if recurrence == 'None':
            dates.append(current_date)
        elif recurrence == 'Daily' or recurrence == 'Weekly' or recurrence == 'Monthly':
            while current_date.date() <= end_date:
                dates.append(current_date)
                if recurrence == 'Daily':
                    current_date += timedelta(days=1)
                elif recurrence == 'Weekly':
                    current_date += timedelta(weeks=1)
                elif recurrence == 'Monthly':
                    current_date += timedelta(days=30)
        else:
            raise ValueError('Invalid recurrence value.')
        return dates

def days_between(start_date, end_date):
    return (end_date - start_date).days

def calculate_invoice_amount(lesson):
    if lesson is None:
        return randint(10, 200)
    if lesson.recurrence == 'None':
        repetitions = 1
    elif lesson.recurrence == 'Daily':
        repetitions = days_between(lesson.date, datetime.combine(lesson.recurrence_end_date, datetime.min.time(), tzinfo=pytz.utc))
    elif lesson.recurrence == 'Weekly':
        repetitions = days_between(lesson.date, datetime.combine(lesson.recurrence_end_date, datetime.min.time(), tzinfo=pytz.utc)) // 7
    elif lesson.recurrence == 'Monthly':
        repetitions = days_between(lesson.date, datetime.combine(lesson.recurrence_end_date, datetime.min.time(), tzinfo=pytz.utc)) // 30
    return lesson.duration * 0.5 * repetitions

def model_is_valid(model):
    try:
        apps.get_model('tutorials', model)
    except LookupError:
        return False
    
    models = ['User', 'Lesson', 'Invoice', 'Notification']
    return model in models

def login_prohibited(view_function):
    """Decorator for view functions that redirect users away if they are logged in."""
    
    def modified_view_function(request):
        if request.user.is_authenticated:
            if request.user.type == 'admin':
                return redirect('admin_dashboard')
            elif request.user.type == 'tutor':
                return redirect('tutor_dashboard')
            else:
                return redirect('student_dashboard')
        else:
            return view_function(request)
    
    return modified_view_function

