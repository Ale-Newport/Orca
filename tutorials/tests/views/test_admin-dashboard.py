import pytest
from django.urls import reverse
from tutorials.models import User, Lesson, Invoice, Notification
from datetime import datetime, timedelta
from django.utils.timezone import now


@pytest.mark.django_db
def test_admin_dashboard_view(client, admin_user, lesson_factory, invoice_factory, notification_factory):
    client.force_login(admin_user)

    # Create test data
    lesson_factory(status='Approved', date=now() + timedelta(days=1))
    lesson_factory(status='Pending', date=now() + timedelta(days=2))
    lesson_factory(status='Rejected', date=now() + timedelta(days=3))

    invoice_factory(paid=True)
    invoice_factory(paid=False)

    notification_factory(is_read=True)
    notification_factory(is_read=False)

    response = client.get(reverse('admin_dashboard'))
    assert response.status_code == 200
    assert response.context['total_lessons'] == 3
    assert response.context['approved_lessons'] == 1
    assert response.context['pending_lessons'] == 1
    assert response.context['rejected_lessons'] == 1
    assert response.context['paid_invoices'] == 1
    assert response.context['unpaid_invoices'] == 1
    assert response.context['read_notifications'] == 1
    assert response.context['unread_notifications'] == 1


@pytest.mark.django_db
def test_list_users(client, admin_user, user_factory):
    client.force_login(admin_user)

    user_factory(type='student')
    user_factory(type='tutor')

    response = client.get(reverse('list_users'))
    assert response.status_code == 200
    assert len(response.context['users']) == 2


@pytest.mark.django_db
def test_create_user_valid(client, admin_user, user_form_data):
    client.force_login(admin_user)

    response = client.post(reverse('create_user'), data=user_form_data)
    assert response.status_code == 302
    assert User.objects.filter(username=user_form_data['username']).exists()


@pytest.mark.django_db
def test_update_user(client, admin_user, user_factory):
    client.force_login(admin_user)

    user = user_factory(username="existing_user")
    response = client.post(reverse('update_user', args=[user.id]), {'username': 'updated_user'})
    assert response.status_code == 302
    assert User.objects.get(id=user.id).username == 'updated_user'


@pytest.mark.django_db
def test_delete_user(client, admin_user, user_factory):
    client.force_login(admin_user)

    user = user_factory(username="delete_me")
    response = client.post(reverse('delete_user', args=[user.id]))
    assert response.status_code == 302
    assert not User.objects.filter(username="delete_me").exists()


@pytest.mark.django_db
def test_list_lessons(client, admin_user, lesson_factory):
    client.force_login(admin_user)

    lesson_factory(status='Approved', date=now() + timedelta(days=1))
    lesson_factory(status='Pending', date=now() + timedelta(days=2))

    response = client.get(reverse('list_lessons'))
    assert response.status_code == 200
    assert len(response.context['lessons']) == 2


@pytest.mark.django_db
def test_create_lesson_valid(client, admin_user, lesson_form_data):
    client.force_login(admin_user)

    response = client.post(reverse('create_lesson'), data=lesson_form_data)
    assert response.status_code == 302
    assert Lesson.objects.filter(subject=lesson_form_data['subject']).exists()


@pytest.mark.django_db
def test_update_lesson(client, admin_user, lesson_factory):
    client.force_login(admin_user)

    lesson = lesson_factory(subject="Old Subject")
    response = client.post(reverse('update_lesson', args=[lesson.id]), {'subject': 'New Subject'})
    assert response.status_code == 302
    assert Lesson.objects.get(id=lesson.id).subject == 'New Subject'


@pytest.mark.django_db
def test_delete_lesson(client, admin_user, lesson_factory):
    client.force_login(admin_user)

    lesson = lesson_factory(subject="Delete Lesson")
    response = client.post(reverse('delete_lesson', args=[lesson.id]))
    assert response.status_code == 302
    assert not Lesson.objects.filter(subject="Delete Lesson").exists()


@pytest.mark.django_db
def test_list_invoices(client, admin_user, invoice_factory):
    client.force_login(admin_user)

    invoice_factory(paid=True)
    invoice_factory(paid=False)

    response = client.get(reverse('list_invoices'))
    assert response.status_code == 200
    assert len(response.context['invoices']) == 2


@pytest.mark.django_db
def test_create_invoice_valid(client, admin_user, invoice_form_data):
    client.force_login(admin_user)

    response = client.post(reverse('create_invoice'), data=invoice_form_data)
    assert response.status_code == 302
    assert Invoice.objects.filter(amount=invoice_form_data['amount']).exists()


@pytest.mark.django_db
def test_delete_invoice(client, admin_user, invoice_factory):
    client.force_login(admin_user)

    invoice = invoice_factory(amount=100.0)
    response = client.post(reverse('delete_invoice', args=[invoice.id]))
    assert response.status_code == 302
    assert not Invoice.objects.filter(amount=100.0).exists()
