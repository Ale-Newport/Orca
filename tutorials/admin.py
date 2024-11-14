from django.contrib import admin
from .models import User, Lesson, Invoice
# Register your models here.
admin.site.register(User)
admin.site.register(Lesson)
admin.site.register(Invoice)