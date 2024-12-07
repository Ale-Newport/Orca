import pytest
from django.urls import reverse
from django.utils.timezone import now
from datetime import datetime, timedelta
from tutorials.models import Lesson


@pytest.mark.django_db
def test_tutor_dashboard_view(client, tutor_user, lesson_factory):
    client.force_login(tutor_user)

    # Create test lessons
    lesson_factory(tutor=tutor_user, date=now() + timedelta(days=1), status='Approved')
    lesson_factory(tutor=tutor_user, date=now() + timedelta(days=2), status='Pending')  # Should not be included

    response = client.get(reverse('tutor_dashboard'))
    assert response.status_code == 200
    assert len(response.context['lessons']) == 1  # Only "Approved" lessons are included


@pytest.mark.django_db
def test_tutor_dashboard_no_lessons(client, tutor_user):
    client.force_login(tutor_user)
    response = client.get(reverse('tutor_dashboard'))
    assert response.status_code == 200
    assert len(response.context['lessons']) == 0  # No lessons available


@pytest.mark.django_db
def test_tutor_lessons_view(client, tutor_user, lesson_factory):
    client.force_login(tutor_user)

    lesson_factory(tutor=tutor_user, date=now() + timedelta(days=1))
    lesson_factory(tutor=tutor_user, date=now() + timedelta(days=2))

    response = client.get(reverse('tutor_lessons'))
    assert response.status_code == 200
    assert len(response.context['lessons']) == 2


@pytest.mark.django_db
def test_tutor_lessons_no_lessons(client, tutor_user):
    client.force_login(tutor_user)
    response = client.get(reverse('tutor_lessons'))
    assert response.status_code == 200
    assert len(response.context['lessons']) == 0


@pytest.mark.django_db
def test_tutor_schedule_current_month(client, tutor_user, lesson_factory):
    client.force_login(tutor_user)

    today = datetime.today()
    lesson_factory(tutor=tutor_user, date=datetime(today.year, today.month, 15))

    response = client.get(reverse('tutor_schedule'))
    assert response.status_code == 200
    assert response.context['month'] == today.month
    assert response.context['year'] == today.year
    assert len(response.context['calendar']) > 0


@pytest.mark.django_db
def test_tutor_schedule_specific_month(client, tutor_user, lesson_factory):
    client.force_login(tutor_user)

    lesson_factory(tutor=tutor_user, date=datetime(2023, 12, 15))

    response = client.get(reverse('tutor_schedule', args=[2023, 12]))
    assert response.status_code == 200
    assert response.context['month'] == 12
    assert response.context['year'] == 2023


@pytest.mark.django_db
def test_tutor_schedule_no_lessons(client, tutor_user):
    client.force_login(tutor_user)

    response = client.get(reverse('tutor_schedule'))
    assert response.status_code == 200
    assert len(response.context['calendar']) > 0  # Calendar should still render
