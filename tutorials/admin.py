from django.contrib import admin
from .models import User, Lesson, Invoice

from django.contrib import admin
from .models import User, Lesson, Invoice

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'date', 'duration', 'tutor', 'status', 'is_assigned')  # Combined fields from both versions
    list_filter = ('status', 'subject', 'date', 'tutor')  # Combined filters from both versions
    search_fields = ('student__username', 'subject', 'tutor')  # Search fields from the first version
    ordering = ('-date',)  # Ordering from the first version
    date_hierarchy = 'date'  # Date hierarchy from the first version
    actions = ['approve_lessons', 'reject_lessons']

    @admin.action(description='Approve selected lessons')
    def approve_lessons(self, request, queryset):
        queryset.update(status='Approved', tutor='Assigned Tutor')
        self.message_user(request, f"{queryset.count()} lessons approved.")

    @admin.action(description='Reject selected lessons')
    def reject_lessons(self, request, queryset):
        queryset.update(status='Rejected')
        self.message_user(request, f"{queryset.count()} lessons rejected.")

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount', 'issued_date', 'due_date', 'paid')
    list_filter = ('paid', 'due_date')
    search_fields = ('student__username',)
    ordering = ('-issued_date',)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)


