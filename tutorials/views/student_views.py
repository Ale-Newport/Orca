from django.contrib.auth.decorators import login_required
from tutorials.decorators import user_type_required
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from tutorials.models import Lesson, Invoice, Notification
from calendar import monthrange
from datetime import datetime
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from tutorials.forms import RequestForm


@login_required
@user_type_required(['student'])
def dashboard(request):
    """Display the student dashboard"""

    # Get student's dashboard data
    user = request.user
    lessons = Lesson.objects.filter(student=user, status="Approved")
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
    return render(request, 'student/dashboard.html', context)

# Lesson views
@login_required
def lessons(request):
    """View all upcoming lessons for the logged-in student."""
    user = request.user
    lessons = Lesson.objects.filter(student=user, status="Approved")
    upcoming_lessons = []
    for lesson in lessons:
        if lesson.is_upcoming():
            upcoming_lessons.append(lesson)
    return render(request, 'student/list_lessons.html', {'lessons': upcoming_lessons})

@login_required
@user_type_required(['student'])
def schedule(request, year=None, month=None):
    """View the student's lesson schedule for the given month."""
    user = request.user
    # Use current year and month if not provided
    today = datetime.today()
    year = year or today.year
    month = month or today.month
    # Get lessons for the given month
    all_lessons = Lesson.objects.filter(student=user, status="Approved")
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
    return render(request, 'student/view_schedule.html', context)


# Lesson request views
@login_required
@user_type_required(['student'])
def requests(request):
    """View all requested lessons for the logged-in student."""
    user = request.user
    lessons = Lesson.objects.filter(student=user).order_by('date')
    return render(request, 'student/list_requests.html', {'lessons': lessons})

@login_required
@user_type_required(['student'])
def create_update_request(request, pk=None):
    """Create or update a lesson request."""
    if pk:
        lesson = get_object_or_404(Lesson, pk=pk, student=request.user)
        form = RequestForm(request.POST or None, instance=lesson)
    else:
        form = RequestForm(request.POST or None, instance=Lesson(student=request.user))

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            if pk:
                messages.success(request, 'Your lesson request has been updated successfully.')
            else:
                messages.success(request, 'Your lesson request has been submitted and is currently pending approval.')
            return HttpResponseRedirect(reverse('student_requests'))
        else:
            messages.error(request, 'There was an error with your submission. Please check the form for details.')

    return render(request, 'student/create_update_request.html', {'form': form})

@login_required
@user_type_required(['student'])
def delete_request(request, pk):
    """Remove an existing lesson for the logged-in user."""
    lesson = get_object_or_404(Lesson, id=pk, student=request.user)
    if request.method == 'GET':
        return render(request, 'student/delete_request.html', {'lesson': lesson})
    elif request.method == 'POST':
        try:
            lesson.delete()
            messages.success(request, 'Your lesson has been successfully removed.')
            return HttpResponseRedirect(reverse('student_requests'))
        except Exception as e:
            messages.error(request, f'There was an error deleting this lesson: {str(e)}')
            return HttpResponseRedirect(reverse('student_requests'))
    else:
        return HttpResponseBadRequest('This URL only supports GET and POST requests.')


# Invoice views
@login_required
@user_type_required(['student'])
def invoices(request):
    """View all invoices for the logged-in student."""
    invoices = Invoice.objects.filter(student=request.user).order_by('-due_date')
    return render(request, 'student/list_invoices.html', {'invoices': invoices})

