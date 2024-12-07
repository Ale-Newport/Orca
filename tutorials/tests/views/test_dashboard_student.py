import pytest
from django.urls import reverse
from django.utils.timezone import now
from datetime import datetime, timedelta
from tutorials.models import Lesson, Invoice

@pytest.mark.django_db
def test_dashboard_authenticated_student(client, student_user, lesson_factory, invoice_factory):
    client.force_login(student_user)

    lesson_factory(student=student_user, date=now() + timedelta(days=1), status="Approved")
    invoice_factory(student=student_user, paid=False)

    response = client.get(reverse('dashboard'))
    assert response.status_code == 200
    assert 'upcoming_lessons' in response.context
    assert 'unpaid_invoices' in response.context


@pytest.mark.django_db
def test_dashboard_unauthenticated(client):
    response = client.get(reverse('dashboard'))
    assert response.status_code == 302  # Redirect to login


@pytest.mark.django_db
def test_dashboard_no_lessons_or_invoices(client, student_user):
    client.force_login(student_user)
    response = client.get(reverse('dashboard'))
    assert response.status_code == 200
    assert not response.context['upcoming_lessons']
    assert not response.context['unpaid_invoices']


@pytest.mark.django_db
def test_schedule_current_month(client, student_user, lesson_factory):
    client.force_login(student_user)

    today = datetime.today()
    lesson_factory(student=student_user, date=datetime(today.year, today.month, 5))

    response = client.get(reverse('schedule'))
    assert response.status_code == 200
    assert response.context['month'] == today.month
    assert response.context['year'] == today.year


@pytest.mark.django_db
def test_schedule_specific_month(client, student_user, lesson_factory):
    client.force_login(student_user)

    lesson_factory(student=student_user, date=datetime(2023, 12, 5))
    response = client.get(reverse('schedule', args=[2023, 12]))
    assert response.status_code == 200
    assert response.context['month'] == 12
    assert response.context['year'] == 2023


@pytest.mark.django_db
def test_requests(client, student_user, lesson_factory):
    client.force_login(student_user)

    lesson_factory(student=student_user, date=now() + timedelta(days=5))
    response = client.get(reverse('requests'))
    assert response.status_code == 200
    assert len(response.context['lessons']) == 1


@pytest.mark.django_db
def test_request_lesson_valid_form(client, student_user, lesson_form_data):
    client.force_login(student_user)
    response = client.post(reverse('request_lesson'), data=lesson_form_data)
    assert response.status_code == 302  # Redirect to 'student_requests'
    assert Lesson.objects.count() == 1


@pytest.mark.django_db
def test_request_lesson_invalid_form(client, student_user):
    client.force_login(student_user)
    response = client.post(reverse('request_lesson'), data={})
    assert response.status_code == 200  # Re-render form with errors
    assert Lesson.objects.count() == 0


@pytest.mark.django_db
def test_request_lesson_overlapping(client, student_user, lesson_factory, lesson_form_data):
    client.force_login(student_user)
    existing_lesson = lesson_factory(student=student_user, date=now() + timedelta(days=1), duration=60)

    lesson_form_data['preferred_date'] = existing_lesson.date
    lesson_form_data['duration'] = 60
    response = client.post(reverse('request_lesson'), data=lesson_form_data)

    assert response.status_code == 200
    assert "overlaps with an existing lesson" in response.content.decode()


@pytest.mark.django_db
def test_update_request_valid(client, student_user, lesson_factory, lesson_form_data):
    client.force_login(student_user)
    lesson = lesson_factory(student=student_user)

    response = client.post(reverse('update_request', args=[lesson.id]), data=lesson_form_data)
    assert response.status_code == 302
    assert Lesson.objects.get(id=lesson.id).subject == lesson_form_data['subject']


@pytest.mark.django_db
def test_delete_request_valid(client, student_user, lesson_factory):
    client.force_login(student_user)
    lesson = lesson_factory(student=student_user)

    response = client.post(reverse('delete_request', args=[lesson.id]))
    assert response.status_code == 302
    assert not Lesson.objects.filter(id=lesson.id).exists()
