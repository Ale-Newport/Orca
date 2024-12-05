from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from tutorials.helpers import login_prohibited
from django.utils import timezone
from tutorials.models import Lesson, Invoice
from calendar import monthrange
from datetime import datetime, timedelta

@login_required
def dashboard(request):
    user = request.user
    upcoming_lessons = Lesson.objects.filter(student=user, date__gte=timezone.now()).order_by('date')[:5]
    context = {
        'user': user,
        'upcoming_lessons': upcoming_lessons,
    }
    return render(request, 'tutor/tutor_dashboard.html', context)

@login_required
def choose_class(request):
    lessons = Lesson.objects.filter(status='Pending').order_by('date')
    return render(request, 'tutor/choose_class.html', {'lessons': lessons})

@login_required
def tutor_schedule(request, year=None, month=None):
    user = request.user

    # Set current year and month as defaults if not provided
    today = datetime.today()
    year = year or today.year
    month = month or today.month

    # Fetch lessons for the specified month and tutor
    lessons = Lesson.objects.filter(
        tutor=user,
        date__year=year,
        date__month=month
    )

    # Determine the number of days in the given month
    days_in_month = monthrange(year, month)[1]

    # Build the calendar data with lessons grouped by day
    calendar = []
    for day in range(1, days_in_month + 1):
        daily_lessons = lessons.filter(date__day=day)
        calendar.append({
            "day": day,
            "lessons": daily_lessons
        })

    # Calculate previous and next month/year for navigation
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    # Prepare context for the template
    context = {
        "calendar": calendar,
        "month": month,
        "year": year,
        "prev_month": prev_month,
        "prev_year": prev_year,
        "next_month": next_month,
        "next_year": next_year,
    }

    return render(request, 'tutor/tutor_schedule.html', context)