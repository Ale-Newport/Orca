from django.shortcuts import redirect
from django.contrib import messages
from .models import Notification, Lesson

def reject_lesson(request, lesson_id):
    lesson = Lesson.objects.get(id=lesson_id)

    # This isa simplified logic for rejecting a lesson
    if lesson:
        # Send a notification to the student
        Notification.objects.create(
            user=lesson.student,  # Assuming `student` is a ForeignKey in Lesson
            message=f"Your lesson request for {lesson.subject} has been rejected. Reason: Scheduling conflict."
        )
        messages.error(request, "Lesson rejected and the student has been notified.")

    return redirect('dashboard')  # Redirect to a relevant page
