"""
URL configuration for code_tutors project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.contrib import admin
from tutorials.views import views, student_views, tutor_views, admin_views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('administrator/', admin.site.urls),

    # Profile management
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),

    # Student
    path('student/dashboard/', student_views.dashboard, name='student_dashboard'),
    path('student/lessons/', student_views.lessons, name='student_lessons'),
    path('student/schedule/', student_views.schedule, name='student_schedule'),
    path('view_schedule/<int:year>/<int:month>/', student_views.schedule, name='student_schedule'),
    path('student/requests/', student_views.requests, name='student_requests'),
    path('student/lesson/request/', student_views.request_lesson, name='request_lesson'),
    path('student/lesson/update/<int:pk>/', student_views.update_request, name='update_request'),
    path('student/lesson/delete/<int:pk>/', student_views.delete_request, name='delete_request'),
    path('student/invoices/', student_views.invoices, name='student_invoices'),

    # Tutor
    path('tutor/dashboard/', tutor_views.dashboard, name='tutor_dashboard'),
    path('tutor/choose_class/', tutor_views.choose_class, name= 'choose_class' ),
    path('tutor/tutor_schedule/', tutor_views.tutor_schedule, name= 'tutor_schedule'),
    path('tutor/tutor_schedule/<int:year>/<int:month>/', tutor_views.tutor_schedule, name= 'tutor_schedule'),

    # Admin
    path('admin/dashboard/', admin_views.dashboard, name='admin_dashboard'),
    path('admin/users/', admin_views.list_users, name='list_users'),
    path('admin/users/create/', admin_views.create_user, name='create_user'),
    path('admin/users/update/<int:pk>/', admin_views.update_user, name='update_user'),
    path('admin/users/delete/<int:pk>/', admin_views.delete_user, name='delete_user'),
    path('admin/lessons/', admin_views.list_lessons, name='list_lessons'),
    path('admin/lessons/create/', admin_views.create_lesson, name='create_lesson'),
    path('admin/lessons/update/<int:pk>/', admin_views.update_lesson, name='update_lesson'),
    path('admin/lessons/update/', admin_views.update_lessons, name='update_lessons'),
    path('admin/lessons/assign_tutor/<int:pk>/', admin_views.assign_tutor, name='assign_tutor'),
    path('admin/lessons/approve_lesson/<int:pk>/', admin_views.approve_lesson, name='approve_lesson'),
    path('admin/lessons/delete/<int:pk>/', admin_views.delete_lesson, name='delete_lesson'),
    path('admin/invoices/', admin_views.list_invoices, name='list_invoices'),
    path('admin/invoices/create/', admin_views.create_invoice, name='create_invoice'),
    path('admin/invoices/update/<int:pk>/', admin_views.update_invoice, name='update_invoice'),
    path('admin/invoices/delete/<int:pk>/', admin_views.delete_invoice, name='delete_invoice'),

]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
