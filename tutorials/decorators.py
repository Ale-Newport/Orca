from functools import wraps
from django.shortcuts import redirect, render
from django.core.exceptions import PermissionDenied

def user_type_required(allowed_types):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.type not in allowed_types:
                return render(request, '403.html', {
                    'message': "You don't have permission to access this page.",
                    'redirect_url': 'tutor_dashboard' if request.user.type == 'tutor' else 'dashboard'
                }, status=403)
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator