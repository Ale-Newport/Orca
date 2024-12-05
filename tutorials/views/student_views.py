from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from tutorials.models import Lesson, Invoice
from calendar import monthrange
from datetime import datetime, timedelta
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from decimal import Decimal
from tutorials.forms import LessonRequestForm
from django.urls import reverse
from tutorials.decorators import user_type_required
from django.contrib.admin.models import LogEntry, ADDITION
from django.utils.timezone import now
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry

@login_required
@user_type_required(['student'])
def dashboard(request):
    """Display the student dashboard"""
    user = request.user
    upcoming_lessons = Lesson.objects.filter(student=user, date__gte=timezone.now(), status="Approved").order_by('date')[:5]
    unpaid_invoices = Invoice.objects.filter(student=user, paid=False)
    context = {
        'user': user,
        'upcoming_lessons': upcoming_lessons,
        'unpaid_invoices': unpaid_invoices,
    }
    return render(request, 'student/dashboard.html', context)

@login_required
@user_type_required(['student'])
def schedule(request, year=None, month=None):
    user = request.user
    # Use current year and month if not provided
    today = datetime.today()
    year = year or today.year
    month = month or today.month
    # Get lessons for the given month
    lessons = Lesson.objects.filter(student=user, date__year=year, date__month=month)

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
    return render(request, 'student/view_schedule.html', context)

@login_required
@user_type_required(['student'])
def requests(request):
    """View all requested lessons for the logged-in student."""
    user = request.user
    lessons = Lesson.objects.filter(student=user, date__gte=timezone.now()).order_by('date')
    return render(request, 'student/list_requests.html', {'lessons': lessons})

@login_required
def lessons(request):
    """View all upcoming lessons for the logged-in student."""
    user = request.user
    lessons = Lesson.objects.filter(student=user, date__gte=timezone.now(), status="Approved").order_by('date')
    return render(request, 'student/list_lessons.html', {'lessons': lessons})


@login_required
@user_type_required(['student'])
def request_lesson(request):
    if request.method == 'POST':
        form = LessonRequestForm(request.POST)
        if form.is_valid():
            try:
                lesson = form.save(commit=False)
                lesson.status = 'Pending'
                lesson.student = request.user
                lesson.date = form.cleaned_data.get('preferred_date')
                
                # Check for overlapping lessons
                lesson_end_time = lesson.date + timedelta(minutes=lesson.duration)
                overlapping_lessons = Lesson.objects.filter(student=lesson.student, date__lt=lesson_end_time, date__gte=lesson.date)
                if overlapping_lessons.exists():
                    overlapping_details = ', '.join([f"{ol.subject} on {ol.date.strftime('%Y-%m-%d %H:%M')}" for ol in overlapping_lessons])
                    messages.error(request, f'The requested lesson time overlaps with an existing lesson: {overlapping_details}')
                    return render(request, 'student/create_request.html', {'form': form})

                lesson.save()

                # Handle recurrence
                recurrence = form.cleaned_data.get('recurrence')
                end_date = form.cleaned_data.get('end_date')
                if recurrence and recurrence != 'None' and end_date:
                    recurrence_map = {'Daily': timedelta(days=1), 'Weekly': timedelta(weeks=1), 'Monthly': timedelta(month=1)}
                    delta = recurrence_map[recurrence]
                    current_date = lesson.date
                    while True:
                        new_date = current_date + delta

                        if new_date.date() > end_date:
                            break
                        
                        lesson_end_time = new_date + timedelta(minutes=lesson.duration)
                        overlapping_lessons = Lesson.objects.filter(student=lesson.student, date__lt=lesson_end_time, date__gte=new_date)
                        if overlapping_lessons.exists():
                            continue

                        if not Lesson.objects.filter(date=new_date).exists():
                            Lesson.objects.create(
                                student=lesson.student,
                                subject=lesson.subject,
                                date=new_date,
                                duration=lesson.duration,
                                tutor=lesson.tutor,
                                status='Pending',
                                notes=lesson.notes,
                            )
                        
                        current_date = new_date

                messages.success(request, 'Your lesson request has been submitted and is currently pending approval.')
                return redirect('student_requests')
            except Exception as e:
                messages.error(request, f'There was an error saving your lesson request: {str(e)}')
                return render(request, 'student/create_request.html', {'form': form})
        else:
            messages.error(request, 'There was an error with your submission. Please check the form for details.')
            return render(request, 'student/create_request.html', {'form': form})
    else:
        form = LessonRequestForm()
    
    return render(request, 'student/create_request.html', {'form': form})


@login_required
@user_type_required(['student'])
def update_request(request, pk):
    """Update the details of an existing lesson."""
    lesson = get_object_or_404(Lesson, id=pk, student=request.user)
    if request.method == 'POST':
        form = LessonRequestForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your lesson has been updated successfully.')
            return HttpResponseRedirect(reverse('student_requests'))
    else:
        form = LessonRequestForm(instance=lesson)
    return render(request, 'student/update_request.html', {'form': form, 'lesson': lesson})


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


@login_required
@user_type_required(['student'])
def invoices(request):
    """View all invoices for the logged-in student."""
    invoices = Invoice.objects.filter(student=request.user).order_by('-issued_date')
    return render(request, 'student/list_invoices.html', {'invoices': invoices})

@login_required
@user_type_required(['student'])
def generate_invoice_for_lesson(lesson):
    """Generate an invoice for the given lesson."""
    amount = Decimal(lesson.duration * 1)  # Example: $1 per minute
    due_date = lesson.date.date() + timedelta(days=7)  # Due in 7 days
    Invoice.objects.create(
        student=lesson.student,
        amount=amount,
        due_date=due_date
    )

@login_required
def update_admin_class_list(request):
    """Handle selected classes and list them in the admin page for review."""
    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_classes')
        if not selected_ids:
            messages.error(request, 'Please select at least one class to proceed.')
            return redirect('choose_class')
        
        try:
            # Filter lessons based on selected IDs
            selected_lessons = Lesson.objects.filter(id__in=selected_ids)
            for lesson in selected_lessons:
                # Update lesson status to "Under Review" (optional, based on your needs)
                lesson.status = 'Under Review'
                lesson.save()

                # Log the change in the admin system
                LogEntry.objects.log_action(
                    user_id=request.user.id,
                    content_type_id=ContentType.objects.get_for_model(lesson).pk,
                    object_id=lesson.id,
                    object_repr=str(lesson),
                    action_flag=ADDITION,
                    change_message=f"Class {lesson.subject} added to admin review."
                )

            messages.success(request, 'Selected classes have been sent to the admin page for review.')
            return redirect('choose_class')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('choose_class')

    # Redirect if accessed via GET
    return redirect('choose_class')