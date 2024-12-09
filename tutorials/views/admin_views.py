from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from tutorials.models import Lesson, Invoice, User, Notification, Subject
from tutorials.forms import UserForm, LessonForm, InvoiceForm, NotificationForm
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from tutorials.decorators import user_type_required
from tutorials.helpers import calculate_invoice_amount, model_is_valid
from django.apps import apps

# Admin dashboard
@login_required
@user_type_required(['admin'])
def dashboard(request):
    """Display the admin dashboard"""

    # Users
    total_users = User.objects.count()
    student_users = User.objects.filter(type='student').count()
    tutor_users = User.objects.filter(type='tutor').count()
    admin_users = User.objects.filter(type='admin').count()

    # Lessons
    total_lessons = Lesson.objects.filter(date__gte=timezone.now()).count()
    approved_lessons = Lesson.objects.filter(status='Approved', date__gte=timezone.now()).count()
    pending_lessons = Lesson.objects.filter(status='Pending', date__gte=timezone.now()).count()
    rejected_lessons = Lesson.objects.filter(status='Rejected', date__gte=timezone.now()).count()

    # Invoice counts
    total_invoices = Invoice.objects.count()
    paid_invoices = Invoice.objects.filter(paid=True).count()
    unpaid_invoices = Invoice.objects.filter(paid=False).count()

    # Notification counts
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

    # Handle filtering
    type_filter = request.GET.get('type')
    if type_filter: users = users.filter(type=type_filter)

    # Handle searching
    search_query = request.GET.get('search')
    if search_query:
        users = users.filter(Q(username__icontains=search_query) | Q(email__icontains=search_query) | Q(first_name__icontains=search_query) | Q(last_name__icontains=search_query))

    # Handle searching
    order_by = request.GET.get('order_by', 'username')
    users = users.order_by(order_by)

    context = {
        'users': users,
        'order_by': order_by,
    }

    return render(request, 'admin/list_users.html', context)

@login_required
@user_type_required(['admin'])
def create_update_user(request, pk=None):
    if pk:
        user = get_object_or_404(User, pk=pk)
        form = UserForm(request.POST or None, instance=user)
    else:
        form = UserForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Your user has been created/updated successfully.')
            return redirect('list_users')
        else:
            messages.error(request, 'There was an error with your submission. Please check the form for details.')

    return render(request, 'admin/create_update_user.html', {'form': form})


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
    duration_filter = request.GET.get('duration')
    recurrece_filter = request.GET.get('recurrence')

    if status_filter: lessons = lessons.filter(status=status_filter)
    if student_filter: lessons = lessons.filter(student__id=student_filter)
    if subject_filter: lessons = lessons.filter(subject=subject_filter)
    if tutor_filter: lessons = lessons.filter(tutor=tutor_filter)
    if duration_filter: lessons = lessons.filter(duration=duration_filter)
    if recurrece_filter: lessons = lessons.filter(recurrence=recurrece_filter)

    # Searching
    search_query = request.GET.get('search')
    if search_query:
        lessons = lessons.filter(Q(student__username__icontains=search_query) | Q(subject__name__icontains=search_query) | Q(tutor__username__icontains=search_query))

    # Ordering
    order_by = request.GET.get('order_by', 'date')
    lessons = lessons.order_by(order_by)

    # Get values for dropdowns
    students_with_lessons = User.objects.filter(id__in=Lesson.objects.filter(date__gte=timezone.now()).values_list('student', flat=True).distinct()).order_by('username')
    subjects = Subject.objects.filter(id__in=Lesson.objects.filter(date__gte=timezone.now()).values_list('subject', flat=True).distinct()).order_by('name')
    tutors_with_lessons = User.objects.filter(id__in=Lesson.objects.filter(date__gte=timezone.now()).values_list('tutor', flat=True).distinct()).order_by('username')
    durations = Lesson.objects.filter(date__gte=timezone.now()).values_list('duration', flat=True).distinct()
    recurrences = Lesson.objects.filter(date__gte=timezone.now()).values_list('recurrence', flat=True).distinct()
    
    context = {'lessons': lessons, 'order_by': order_by, 'students_with_lessons': students_with_lessons, 'subjects': subjects, 'tutors_with_lessons': tutors_with_lessons, 'durations': durations, 'recurrences': recurrences}

    return render(request, 'admin/list_lessons.html', context)

@login_required
@user_type_required(['admin'])
def create_update_lesson(request, pk=None):
    """Create or update a lesson."""
    if pk:
        lesson = get_object_or_404(Lesson, pk=pk)
        form = LessonForm(request.POST or None, instance=lesson)
    else:
        form = LessonForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Your lesson has been created/updated successfully.')
            return redirect('list_lessons')
        else:
            messages.error(request, 'There was an error with your submission. Please check the form for details.')

    return render(request, 'admin/create_update_lesson.html', {'form': form})


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
    order_by = request.GET.get('order_by', 'due_date')
    invoices = invoices.order_by(order_by)

    # Get distinct values for dropdowns
    students = User.objects.filter(id__in=Invoice.objects.values_list('student', flat=True).distinct()).order_by('username')

    context = {
        'invoices': invoices,
        'order_by': order_by,
        'students': students,
    }

    return render(request, 'admin/list_invoices.html', context)

# Handles invoice creation
@login_required
@user_type_required(['admin'])
def create_update_invoice(request, pk=None):
    if pk:
        invoice = get_object_or_404(Invoice, pk=pk)
        form = InvoiceForm(request.POST or None, instance=invoice)
    else:
        model_name = request.GET.get('model')
        pk = request.GET.get('pk')
        
        if model_name and pk:
            model = apps.get_model('tutorials', model_name)
            obj = get_object_or_404(model, pk=pk)
            
            student, lesson, amount, due_date, paid = None, None, 0, None, False
            if model_name == 'Lesson':
                student = obj.student
                lesson = obj
                amount = calculate_invoice_amount(obj)
                due_date = obj.date
            elif model_name == 'User':
                student = obj
            elif model_name == 'Notification':
                student = obj.user
            else:
                pass
            
            initial_data = {'student': student, 'lesson': lesson, 'amount': amount, 'due_date': due_date, 'paid': paid}
        else:
            initial_data = {}
        
        form = InvoiceForm(request.POST or None, initial=initial_data)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('list_invoices')
        else:
            messages.error(request, 'There was an error with your submission. Please check the form for details.')

    return render(request, 'admin/create_update_invoice.html', {'form': form})


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
    users = User.objects.filter(id__in=Notification.objects.values_list('user', flat=True).distinct()).order_by('username')
    
    context = {
        'notifications': notifications,
        'order_by': order_by,
        'users': users,
    }

    return render(request, 'admin/list_notifications.html', context)

# Notification handling
@login_required
@user_type_required(['admin'])
def create_notification(request):
    model_name = request.GET.get('model')
    pk = request.GET.get('pk')
    
    if model_name and pk:
        model = apps.get_model('tutorials', model_name)
        obj = get_object_or_404(model, pk=pk)
        
        if model_name == 'Invoice':
            user = obj.student
            if obj.paid:
                message = f"Your invoice {obj.pk} for {obj.amount} has been paid"
            elif obj.is_overdue():
                message = f"You have faild to pay your invoice {obj.pk} for {obj.amount} before {obj.due_date.strftime('%d/%m/%Y')} and it is now overdue, this may affect your ability to book lessons"
            else:
                message = f"Reminder that you need to pay your invoice {obj.pk} for {obj.amount} before {obj.date.strftime('%d/%m/%Y at %H:%M')}"
        elif model_name == 'Lesson':
            user = obj.student
            if obj.status == 'Approved' and obj.is_assigned:
                message = f"Your lesson request for {obj.subject} on {obj.date.strftime('%d/%m/%Y at %H:%M')} has been approved with {obj.tutor}"
            elif obj.status == 'Approved' and not obj.is_assigned:
                message = f"Your lesson request for {obj.subject} on {obj.date.strftime('%d/%m/%Y at %H:%M')} has been approved, but no tutor has been assigned yet"
            elif obj.status == 'Pending':
                message = f"Your lesson request for {obj.subject} on {obj.date.strftime('%d/%m/%Y at %H:%M')} is currently pending approval"
            elif obj.status == 'Rejected':
                message = f"Your lesson request for {obj.subject} on {obj.date.strftime('%d/%m/%Y at %H:%M')} has been rejected"
        elif model_name == 'User':
            user = obj
            message = ""
        else:
            user = None
            message = ""
        
        initial_data = {'user': user, 'message': message}
    else:
        initial_data = {}

    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            form.save()
            if model_is_valid(model_name):
                return redirect(f'list_{model_name.lower()}s')
            else:
                return redirect('list_notifications')
    else:
        form = NotificationForm(initial=initial_data)
    
    return render(request, 'admin/create_notification.html', {'form': form})

# Delete notifications
@login_required
@user_type_required(['admin'])
def delete_object(request, model_name, pk):
    model = apps.get_model('tutorials', model_name)
    obj = get_object_or_404(model, pk=pk)
    if request.method == 'POST':
        obj.delete()
        return redirect(f'list_{model_name.lower()}s')
    return render(request, 'admin/delete_object.html', {'object': obj, 'model_name': model_name.lower()})