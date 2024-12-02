from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from tutorials.models import Lesson, Invoice, User

@login_required
def admin_dashboard(request):
    """Display the admin dashboard."""
    total_users = User.objects.count()
    total_lessons = Lesson.objects.count()
    total_invoices = Invoice.objects.count()
    unpaid_invoices = Invoice.objects.filter(paid=False).count()
    context = {
        'total_users': total_users,
        'total_lessons': total_lessons,
        'total_invoices': total_invoices,
        'unpaid_invoices': unpaid_invoices,
    }
    return render(request, 'admin_dashboard.html', context)