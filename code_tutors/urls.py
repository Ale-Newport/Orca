from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from tutorials.views import views, student_views, tutor_views, admin_views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),

    # Profile management
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    path('user/notifications/', views.notifications, name='notifications'),
    path('user/notifications/mark_read/<int:pk>/', views.mark_notification_read, name='mark_notification_read'),

    # Student
    path('student/dashboard/', student_views.dashboard, name='student_dashboard'),
    path('student/lessons/', student_views.lessons, name='student_lessons'),
    path('student/schedule/', student_views.schedule, name='student_schedule'),
    path('student/schedule/<int:year>/<int:month>/', student_views.schedule, name='student_schedule'),
    path('student/requests/', student_views.requests, name='student_requests'),
    path('student/lesson/request/', student_views.create_update_request, name='create_request'),
    path('student/lesson/update/<int:pk>/', student_views.create_update_request, name='update_request'),
    path('student/lesson/delete/<int:pk>/', student_views.delete_request, name='delete_request'),
    path('student/invoices/', student_views.invoices, name='student_invoices'),

    # Tutor
    path('tutor/dashboard/', tutor_views.dashboard, name='tutor_dashboard'),
    path('tutor/lessons/', tutor_views.lessons, name= 'tutor_lessons' ),
    path('tutor/schedule/', tutor_views.schedule, name= 'tutor_schedule'),
    path('tutor/schedule/<int:year>/<int:month>/', tutor_views.schedule, name= 'tutor_schedule'),

    # Admin
    path('admin/dashboard/', admin_views.dashboard, name='admin_dashboard'),
    path('admin/users/', admin_views.list_users, name='list_users'),
    path('admin/users/create/', admin_views.create_update_user, name='create_user'),
    path('admin/users/update/<int:pk>/', admin_views.create_update_user, name='update_user'),
    path('admin/lessons/', admin_views.list_lessons, name='list_lessons'),
    path('admin/lessons/create/', admin_views.create_update_lesson, name='create_lesson'),
    path('admin/lessons/update/<int:pk>/', admin_views.create_update_lesson, name='update_lesson'),
    path('admin/invoices/', admin_views.list_invoices, name='list_invoices'),
    path('admin/invoices/create/', admin_views.create_update_invoice, name='create_invoice'),
    path('admin/invoices/update/<int:pk>/', admin_views.create_update_invoice, name='update_invoice'),
    path('admin/notifications/', admin_views.list_notifications, name='list_notifications'),
    path('admin/notifications/create/', admin_views.create_notification, name='create_notification'),
    path('admin/delete/<str:model_name>/<int:pk>/', admin_views.delete_object, name='delete_object'),

]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
