from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from tutorials.helpers import login_prohibited
from django.utils import timezone
from tutorials.models import Lesson, Invoice
from calendar import monthrange
from datetime import datetime, timedelta
from django.contrib import messages
from tutorials.decorators import user_type_required


@login_required
@user_type_required(['tutor'])
def dashboard(request):
    user = request.user
    lessons = Lesson.objects.filter(tutor=user, date__gte=timezone.now(), status='Approved').order_by('date')[:5]
    context = {
        'user': user,
        'lessons': lessons,
    }
    return render(request, 'tutor/tutor_dashboard.html', context)


@login_required
@user_type_required(['tutor'])
def lessons(request):
    user = request.user
    lessons = Lesson.objects.filter(tutor=user, date__gte=timezone.now()).order_by('date')
    return render(request, 'tutor/tutor_lessons.html', {'lessons': lessons})

@login_required
@user_type_required(['tutor'])
def schedule(request, year=None, month=None):
    user = request.user
     # Use current year and month if not provided
    today = datetime.today()
    year = year or today.year
    month = month or today.month
    # Get lessons for the given month
    lessons = Lesson.objects.filter(tutor=user, date__year=year, date__month=month)

    # Generate calendar structure
    days_in_month = monthrange(year, month)[1]
    first_day_of_month = datetime(year, month, 1).weekday()
    calendar = []
    week = [None] * first_day_of_month

    for day in range(1, days_in_month + 1):
        day_lessons = [lesson for lesson in lessons if lesson.date.day == day]
        week.append({"day": day, "lessons": day_lessons})
        if len(week) == 7:
            calendar.append(week)
            week = []

    if week:
        week.extend([None] * (7 - len(week)))
        calendar.append(week)

    context = {
        "calendar": calendar,
        "month": month,
        "year": year,
        "prev_month": (month - 1) if month > 1 else 12,
        "prev_year": year if month > 1 else year - 1,
        "next_month": (month + 1) if month < 12 else 1,
        "next_year": year if month < 12 else year + 1,
    }
    return render(request, 'tutor/tutor_schedule.html', context)
