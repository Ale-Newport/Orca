from functools import wraps
from django.shortcuts import redirect, render
from django.core.exceptions import PermissionDenied

# Access control based on the type of user
def user_type_required(allowed_types):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            # Redirect to login if the user is not authenticated
            if not request.user.is_authenticated:
                return redirect('log_in')

            # Return 403  if user type is not allowed
            if request.user.type not in allowed_types:
                return render(request, '403.html', {
                    'message': "You don't have permission to access this page.", 
                    'redirect_url': 'student_dashboard' if request.user.type == 'student' else 'tutor_dashboard'
                }, status=403)
                
            # Allow access if user type is permitted
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator
