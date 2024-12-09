from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from tutorials.models import Lesson, Notification
from calendar import monthrange
from datetime import datetime
from tutorials.decorators import user_type_required

# Display tutor dashboard with upcoming lessons
@login_required
@user_type_required(['tutor'])
def dashboard(request):
    """Display the tutor dashboard"""
    user = request.user
    lessons = Lesson.objects.filter(tutor=user, status="Approved")
    upcoming_lessons = []
    for lesson in lessons:
        if lesson.is_upcoming():
            upcoming_lessons.append(lesson)
    unread_notifications = Notification.objects.filter(user=user, is_read=False)
    
    context = {
        'user': user,
        'upcoming_lessons': upcoming_lessons,
        'unread_notifications': unread_notifications,
    }
    
    return render(request, 'tutor/tutor_dashboard.html', context)


@login_required
@user_type_required(['tutor'])
def lessons(request):
    """View all upcoming lessons for the logged-in tutor."""
    user = request.user
    lessons = Lesson.objects.filter(tutor=user, status="Approved")
    upcoming_lessons = []
    for lesson in lessons:
        if lesson.is_upcoming():
            upcoming_lessons.append(lesson)
    return render(request, 'tutor/tutor_lessons.html', {'lessons': upcoming_lessons})

# monthly calendar view
@login_required
@user_type_required(['tutor'])
def schedule(request, year=None, month=None):
    user = request.user
     # Use current year and month if not provided
    today = datetime.today()
    year = year or today.year
    month = month or today.month
    # Get lessons for the given month
    all_lessons = Lesson.objects.filter(tutor=user, status="Approved")
    lessons = []
    for lesson in all_lessons:
        for date in lesson.lesson_dates():
            if date.year == year and date.month == month:
                lessons.append(lesson)

    # Generate calendar structure
    days_in_month = monthrange(year, month)[1]
    first_day_of_month = datetime(year, month, 1).weekday()
    calendar = []
    week = [None] * first_day_of_month

    for day in range(1, days_in_month + 1):
        day_lessons = [lesson for lesson in lessons if any(date.date() == datetime(year, month, day).date() for date in lesson.lesson_dates())]
        day_lessons = list(set(day_lessons))
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
