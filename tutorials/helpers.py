from django.shortcuts import redirect

def login_prohibited(view_function):
    """Decorator for view functions that redirect users away if they are logged in."""
    
    def modified_view_function(request):
        if request.user.is_authenticated:
            if request.user.type == 'admin':
                return redirect('admin_dashboard')
            elif request.user.type == 'tutor':
                return redirect('tutor_dashboard')
            else:
                return redirect('student_dashboard')
        else:
            return view_function(request)
    
    return modified_view_function

def admin_user_required(view_function):
    """Decorator for view functions that redirect users away if they are not admins."""
    
    def modified_view_function(request):
        if request.user.type == 'admin':
            return view_function(request)
        else:
            if request.user.type == 'tutor':
                return redirect('tutor_dashboard')
            elif request.user.type == 'student':
                return redirect('student_dashboard')
            else:
                return redirect('log_in')
    
    return modified_view_function

def tutor_user_required(view_function):
    """Decorator for view functions that redirect users away if they are not tutors."""
    
    def modified_view_function(request):
        if request.user.type == 'tutors':
            return view_function(request)
        else:
            if request.user.type == 'admin':
                return redirect('admin_dashboard')
            elif request.user.type == 'student':
                return redirect('student_dashboard')
            else:
                return redirect('log_in')
    
    return modified_view_function

def student_user_required(view_function):
    """Decorator for view functions that redirect users away if they are not students."""
    
    def modified_view_function(request):
        if request.user.type == 'students':
            return view_function(request)
        else:
            if request.user.type == 'admin':
                return redirect('admin_dashboard')
            elif request.user.type == 'tutor':
                return redirect('tutor_dashboard')
            else:
                return redirect('log_in')
    
    return modified_view_function
