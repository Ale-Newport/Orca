from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from tutorials.models import Lesson, Invoice, User, Notification
from tutorials.forms import UserFormAdmin, LessonForm, InvoiceForm, NotificationForm
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from datetime import datetime, timedelta
from tutorials.decorators import user_type_required

@login_required
@user_type_required(['admin'])
def dashboard(request):
    """Display the admin dashboard"""
    total_users = User.objects.count()
    student_users = User.objects.filter(type='student').count()
    tutor_users = User.objects.filter(type='tutor').count()
    admin_users = User.objects.filter(type='admin').count()
    total_lessons = Lesson.objects.filter(date__gte=timezone.now()).count()
    approved_lessons = Lesson.objects.filter(status='Approved', date__gte=timezone.now()).count()
    pending_lessons = Lesson.objects.filter(status='Pending', date__gte=timezone.now()).count()
    rejected_lessons = Lesson.objects.filter(status='Rejected', date__gte=timezone.now()).count()
    total_invoices = Invoice.objects.count()
    paid_invoices = Invoice.objects.filter(paid=True).count()
    unpaid_invoices = Invoice.objects.filter(paid=False).count()
    total_notifications = Notification.objects.count()
    read_notifications = Notification.objects.filter(is_read=True).count()
    unread_notifications = Notification.objects.filter(is_read=False).count()

    context = {
        'total_users': total_users,
        'student_users': student_users,
        'tutor_users': tutor_users,
        'admin_users': admin_users,
        'total_lessons': total_lessons,
        'approved_lessons': approved_lessons,
        'pending_lessons': pending_lessons,
        'rejected_lessons': rejected_lessons,
        'total_invoices': total_invoices,
        'unpaid_invoices': unpaid_invoices,
        'paid_invoices': paid_invoices,
        'total_notifications': total_notifications,
        'read_notifications': read_notifications,
        'unread_notifications': unread_notifications,
    }
    return render(request, 'admin/admin_dashboard.html', context)

# User views
@login_required
@user_type_required(['admin'])
def list_users(request):
    users = User.objects.all()

    # Filtering
    type_filter = request.GET.get('type')
    if type_filter: users = users.filter(type=type_filter)

    # Searching
    search_query = request.GET.get('search')
    if search_query:
        users = users.filter(Q(username__icontains=search_query) | Q(email__icontains=search_query) | Q(first_name__icontains=search_query) | Q(last_name__icontains=search_query))

    # Ordering
    order_by = request.GET.get('order_by', 'username')
    users = users.order_by(order_by)

    context = {
        'users': users,
        'order_by': order_by,
    }

    return render(request, 'admin/list_users.html', context)

@login_required
@user_type_required(['admin'])
def create_user(request):
    if request.method == 'POST':
        form = UserFormAdmin(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_users')
    else:
        form = UserFormAdmin()
    return render(request, 'admin/create_user.html', {'form': form})

@login_required
@user_type_required(['admin'])
def update_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserFormAdmin(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('list_users')
    else:
        form = UserFormAdmin(instance=user)
    return render(request, 'admin/update_user.html', {'form': form})

@login_required
@user_type_required(['admin'])
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        return redirect('list_users')
    return render(request, 'admin/delete_user.html', {'user': user})

# Lesson views
@login_required
@user_type_required(['admin'])
def list_lessons(request):
    lessons = Lesson.objects.filter(date__gte=timezone.now())

    # Filtering
    status_filter = request.GET.get('status')
    student_filter = request.GET.get('student')
    subject_filter = request.GET.get('subject')
    tutor_filter = request.GET.get('tutor')
    date_filter = request.GET.get('date')
    duration_filter = request.GET.get('duration')

    if status_filter: lessons = lessons.filter(status=status_filter)
    if student_filter: lessons = lessons.filter(student__id=student_filter)
    if subject_filter: lessons = lessons.filter(subject=subject_filter)
    if tutor_filter: lessons = lessons.filter(tutor=tutor_filter)
    if date_filter: lessons = lessons.filter(date__date=date_filter)
    if duration_filter: lessons = lessons.filter(duration=duration_filter)

    # Searching
    search_query = request.GET.get('search')
    if search_query:
        lessons = lessons.filter(Q(student__username__icontains=search_query) | Q(subject__icontains=search_query) | Q(tutor__icontains=search_query))

    # Ordering
    order_by = request.GET.get('order_by', 'date')
    lessons = lessons.order_by(order_by)

    # Get values for dropdowns
    students = User.objects.filter(type='student').distinct()
    students_with_lessons = Lesson.objects.filter(date__gte=timezone.now()).values_list('student', flat=True).distinct()
    students_with_lessons = User.objects.filter(id__in=students_with_lessons)
    subjects = Lesson.objects.filter(date__gte=timezone.now()).values_list('subject', flat=True).distinct()
    tutors = User.objects.filter(type='tutor').distinct()
    tutors_with_lessons = Lesson.objects.filter(date__gte=timezone.now()).values_list('tutor', flat=True).distinct()
    durations = Lesson.objects.filter(date__gte=timezone.now()).values_list('duration', flat=True).distinct()
    
    context = {'lessons': lessons, 'order_by': order_by, 'students': students, 'students_with_lessons': students_with_lessons, 'subjects': subjects, 'tutors': tutors, 'tutors_with_lessons': tutors_with_lessons, 'durations': durations}

    return render(request, 'admin/list_lessons.html', context)

@login_required
@user_type_required(['admin'])
def create_lesson(request):
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            try:
                lesson = form.save(commit=False)
                lesson.status = 'Approved'
                
                # Check for overlapping lessons
                lesson_end_time = lesson.date + timedelta(minutes=lesson.duration)
                overlapping_lessons = Lesson.objects.filter(student=lesson.student, date__lt=lesson_end_time, date__gte=lesson.date)
                if overlapping_lessons.exists():
                    overlapping_details = ', '.join([f"{ol.subject} on {ol.date.strftime('%Y-%m-%d %H:%M')}" for ol in overlapping_lessons])
                    messages.error(request, f'The lesson time overlaps with an existing lesson: {overlapping_details}')
                    return render(request, 'admin/create_lesson.html', {'form': form})

                lesson.save()

                messages.success(request, 'Your lesson has been created and approved.')
                return redirect('list_lessons')
            except Exception as e:
                messages.error(request, f'There was an error saving your lesson: {str(e)}')
                return render(request, 'admin/create_lesson.html', {'form': form})
        else:
            messages.error(request, 'There was an error with your submission. Please check the form for details.')
            return render(request, 'admin/create_lesson.html', {'form': form})
    else:
        form = LessonForm()
    
    return render(request, 'admin/create_lesson.html', {'form': form})

@login_required
@user_type_required(['admin'])
def update_lesson(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    if request.method == 'POST':
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            return redirect('list_lessons')
    else:
        form = LessonForm(instance=lesson)
    return render(request, 'admin/update_lesson.html', {'form': form})

@login_required
@user_type_required(['admin'])
def delete_lesson(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    if request.method == 'POST':
        lesson.delete()
        return redirect('list_lessons')
    return render(request, 'admin/delete_lesson.html', {'lesson': lesson})


# Invoice views
@login_required
@user_type_required(['admin'])
def list_invoices(request):
    invoices = Invoice.objects.all()

    # Filtering
    paid_filter = request.GET.get('paid')
    student_filter = request.GET.get('student')

    if paid_filter: invoices = invoices.filter(paid=(paid_filter == 'True'))
    if student_filter: invoices = invoices.filter(student__id=student_filter)

    # Searching
    search_query = request.GET.get('search')
    if search_query:
        invoices = invoices.filter(Q(student__username__icontains=search_query) | Q(amount__icontains=search_query))

    # Ordering
    order_by = request.GET.get('order_by', 'issued_date')
    invoices = invoices.order_by(order_by)

    # Get distinct values for dropdowns
    students = Invoice.objects.values_list('student', flat=True).distinct()
    students = User.objects.filter(id__in=students)

    context = {
        'invoices': invoices,
        'order_by': order_by,
        'students': students,
    }

    return render(request, 'admin/list_invoices.html', context)

@login_required
@user_type_required(['admin'])
def create_invoice(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_invoices')
    else:
        form = InvoiceForm()
    return render(request, 'admin/create_invoice.html', {'form': form})

@login_required
@user_type_required(['admin'])
def update_invoice(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            return redirect('list_invoices')
    else:
        form = InvoiceForm(instance=invoice)
    return render(request, 'admin/update_invoice.html', {'form': form})

@login_required
@user_type_required(['admin'])
def delete_invoice(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        invoice.delete()
        return redirect('list_invoices')
    return render(request, 'admin/delete_invoice.html', {'invoice': invoice})


# Notification views
@login_required
@user_type_required(['admin'])
def list_notifications(request):
    notifications = Notification.objects.all()

    # Filtering
    status_filter = request.GET.get('is_read')
    user_filter = request.GET.get('user')

    if status_filter: notifications = notifications.filter(is_read=status_filter)
    if user_filter: notifications = notifications.filter(user__id=user_filter)

    # Searching
    search_query = request.GET.get('search')
    if search_query:
        notifications = notifications.filter(Q(user__username__icontains=search_query) | Q(message__icontains=search_query))

    # Ordering
    order_by = request.GET.get('order_by', 'created_at')
    notifications = notifications.order_by(order_by)

    # Get distinct values for dropdowns
    users = Notification.objects.values_list('user', flat=True).distinct()
    users = User.objects.filter(id__in=users)

    context = {
        'notifications': notifications,
        'order_by': order_by,
        'users': users,
    }

    return render(request, 'admin/list_notifications.html', context)

@login_required
@user_type_required(['admin'])
def create_notification(request):
    user_id = request.GET.get('user')
    message = request.GET.get('message')
    
    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_notifications')
    else:
        initial_data = {}
        if user_id:
            initial_data['user'] = get_object_or_404(User, pk=user_id)
        if message:
            initial_data['message'] = message
        form = NotificationForm(initial=initial_data)
    
    return render(request, 'admin/create_notification.html', {'form': form})

@login_required
@user_type_required(['admin'])
def delete_notification(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    if request.method == 'POST':
        notification.delete()
        return redirect('list_notifications')
    return render(request, 'admin/delete_notification.html', {'notification': notification})
