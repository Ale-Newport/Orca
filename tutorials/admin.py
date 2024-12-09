from django.contrib import admin
from tutorials.models import User, Lesson, Invoice, Notification

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'type', 'get_subjects')
    list_filter = ('type',)
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'date', 'duration', 'tutor', 'status', 'recurrence', 'recurrence_end_date')
    list_filter = ('status', 'subject', 'date', 'recurrence')
    search_fields = ('student__username', 'subject', 'tutor__username')
    ordering = ('-date',)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount', 'due_date', 'paid')
    list_filter = ('paid', 'due_date')
    search_fields = ('student__username',)
    ordering = ('-due_date',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username',)
    ordering = ('-created_at',)