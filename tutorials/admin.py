from django.contrib import admin
from .models import User, Lesson, Invoice

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'date', 'duration', 'tutor', 'status', 'is_assigned')
    list_filter = ('status', 'subject', 'date', 'tutor')
    search_fields = ('student__username', 'subject', 'tutor')
    ordering = ('-date',)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount', 'issued_date', 'due_date', 'paid')
    list_filter = ('paid', 'due_date')
    search_fields = ('student__username',)
    ordering = ('-issued_date',)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'type')
    list_filter = ('type',)
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
