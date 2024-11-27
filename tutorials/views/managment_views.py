from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from tutorials.models import Lesson, Invoice
from datetime import timedelta
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from decimal import Decimal
from tutorials.forms import LessonRequestForm
from django.utils import timezone
from django.urls import reverse



@login_required
def view_upcoming_lessons(request):
    """View all upcoming lessons for the logged-in user."""
    user = request.user
    upcoming_lessons = Lesson.objects.filter(student=user, date__gte=timezone.now(), status="Approved").order_by('date')
    return render(request, 'view_upcoming_lessons.html', {'upcoming_lessons': upcoming_lessons})


@login_required
def request_lesson(request):
    if request.method == 'POST':
        form = LessonRequestForm(request.POST)
        if form.is_valid():
            try:
                lesson = form.save(commit=False)
                lesson.status = 'Pending'
                lesson.student = request.user

                # Assuming your form has a 'date' field that combines date and time.
                preferred_date = form.cleaned_data.get('preferred_date')
                if preferred_date:
                    lesson.date = preferred_date
                else:
                    form.add_error(None, 'A valid date and time are required.')
                    return render(request, 'request_lesson.html', {'form': form})

                # Save the initial lesson
                lesson.save()

                # Handle recurrence
                recurrence = form.cleaned_data.get('recurrence')
                if recurrence and recurrence != 'None':
                    recurrence_map = {
                        'Daily': 1,
                        'Weekly': 7,
                        'Monthly': 30,
                    }
                    delta = recurrence_map[recurrence]
                    for i in range(1, 10):  # Assuming a maximum of 10 recurring sessions
                        new_date = lesson.date + timedelta(days=delta * i)
                        if not Lesson.objects.filter(date=new_date, subject=lesson.subject).exists():
                            Lesson.objects.create(
                                student=lesson.student,
                                subject=lesson.subject,
                                date=new_date,
                                duration=lesson.duration,
                                tutor=lesson.tutor,
                                status='Pending',
                                notes=lesson.notes,
                            )

                messages.success(request, 'Your lesson request has been submitted and is currently pending approval.')
                return redirect('lesson_requests')
            except Exception as e:
                messages.error(request, f'There was an error saving your lesson request: {str(e)}')
                return render(request, 'request_lesson.html', {'form': form})
        else:
            messages.error(request, 'There was an error with your submission. Please check the form for details.')
            return render(request, 'request_lesson.html', {'form': form})
    else:
        form = LessonRequestForm()
    return render(request, 'request_lesson.html', {'form': form})


@login_required
def update_lesson(request, pk):
    """Update the details of an existing lesson."""
    lesson = get_object_or_404(Lesson, id=pk, student=request.user)
    if request.method == 'POST':
        form = LessonRequestForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            #messages.success(request, 'Your lesson has been updated successfully.')
            return HttpResponseRedirect(reverse('view_upcoming_lessons'))
    else:
        form = LessonRequestForm(instance=lesson)
    return render(request, 'update_lesson.html', {'form': form, 'lesson': lesson})


@login_required
def remove_lesson(request, pk):
    """Remove an existing lesson for the logged-in user."""
    lesson = get_object_or_404(Lesson, id=pk, student=request.user)
    if request.method == 'GET':
        return render(request, 'confirm_delete_lesson.html', {'lesson': lesson})
    elif request.method == 'POST':
        try:
            lesson.delete()
            messages.success(request, 'Your lesson has been successfully removed.')
            return HttpResponseRedirect(reverse('view_upcoming_lessons'))
        except Exception as e:
            messages.error(request, f'There was an error deleting this lesson: {str(e)}')
            return HttpResponseRedirect(reverse('view_upcoming_lessons'))
    else:
        return HttpResponseBadRequest('This URL only supports GET and POST requests.')
    

@login_required
def generate_invoice_for_lesson(lesson):
    """Generate an invoice for the given lesson."""
    amount = Decimal(lesson.duration * 10)  # Example: $10 per minute
    due_date = lesson.date.date() + timedelta(days=7)  # Due in 7 days
    Invoice.objects.create(
        student=lesson.student,
        amount=amount,
        due_date=due_date
    )


@login_required
def invoices(request):
    """View all invoices for the logged-in user."""
    user_invoices = Invoice.objects.filter(student=request.user).order_by('-issued_date')
    return render(request, 'invoices.html', {'invoices': user_invoices})

