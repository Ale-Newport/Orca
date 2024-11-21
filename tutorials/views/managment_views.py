
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
    upcoming_lessons = Lesson.objects.filter(student=user, date__gte=timezone.now()).order_by('date')
    return render(request, 'view_upcoming_lessons.html', {'upcoming_lessons': upcoming_lessons})


@login_required
def request_lesson(request):
    if request.method == 'GET':
        form = LessonRequestForm()
        return render(request, 'request_lesson.html', {'form': form})
    elif request.method == 'POST':
        form = LessonRequestForm(request.POST)
        if form.is_valid():
            try:
                lesson = form.save(commit=False)
                lesson.status = 'Pending'

                # Assuming your form has a 'date' field that combines date and time.
                preferred_date = form.cleaned_data.get('date')
                if preferred_date:
                    lesson.date = preferred_date
                else:
                    form.add_error(None, 'A valid date and time are required.')
                    return render(request, 'request_lesson.html', {'form': form})

                # Set the student to the logged-in user
                lesson.student = request.user

                # Save the lesson to the database
                lesson.save()

                # Generate Invoice for the lesson
                generate_invoice_for_lesson(lesson)

                messages.success(request, 'Your lesson request has been submitted and is currently pending approval. An invoice has been generated.')
                return HttpResponseRedirect(reverse('view_upcoming_lessons'))
            
            except Exception as e:
                # Log the exception to see if there are any save errors
                print(f"Error saving lesson: {e}")
                messages.error(request, 'There was an error saving your lesson request. Please try again.')
                return render(request, 'request_lesson.html', {'form': form})
        else:
            # Debugging form errors if the form is invalid
            print(f"Form Errors: {form.errors.as_json()}")  # Full details of form errors
            messages.error(request, 'There was an error with your submission. Please check the form for details.')
            return render(request, 'request_lesson.html', {'form': form})
    else:
        return HttpResponse(status=405)  # Method Not Allowed for unsupported request methods


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

