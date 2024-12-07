from .views import LoginProhibitedMixin, LogInView, home, log_out
from .student_views import dashboard as student_dashboard
from .tutor_views import dashboard as tutor_dashboard
from .admin_views import dashboard as admin_dashboard

__all__ = [
    'LoginProhibitedMixin',
    'LogInView',
    'home',
    'log_out',
    'student_dashboard',
    'tutor_dashboard',
    'admin_dashboard'
]