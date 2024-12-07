from django.core.management.base import BaseCommand, CommandError
from tutorials.models import User, Subject, Lesson, Invoice, Notification
from django.utils.timezone import now
from datetime import datetime, timedelta
import pytz
from faker import Faker
from random import randint, choices, random


class Command(BaseCommand):
    """Build automation command to seed the database."""

    USER_COUNT = 500
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'
    SUBJECT_CHOICES = [
        ('Python', 'Python'),
        ('Java', 'Java'),
        ('C++', 'C++'),
        ('Scala', 'Scala'),
        ('Web Development', 'Web Development'),
    ]

    def __init__(self):
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_subjects()
        self.subjects = Subject.objects.all()
        self.create_users()
        self.users = User.objects.all()
        self.create_lessons()
        self.lessons = Lesson.objects.all()
        self.create_invoices()
        self.invoices = Invoice.objects.all()
        self.create_notifications()
        self.invoices = Invoice.objects.all()

    # Subject seeding
    def create_subjects(self):
        for subject in Subject.SUBJECT_CHOICES:
            Subject.objects.get_or_create(name=subject[0])
    

    # User seeding
    def create_users(self):
        self.generate_user_fixtures()
        self.generate_random_users()

    def generate_user_fixtures(self):
        user_fixtures = [
            {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe', 'type': 'admin'},
            {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe', 'type': 'tutor', 'subjects': ['Python', 'Java']},
            {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson', 'type': 'student'},
        ]
        for data in user_fixtures:
            self.create_user(data)

    def generate_random_users(self):
        user_count = User.objects.count()
        while user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user()
            user_count = User.objects.count()
        print("User seeding complete.      ")

    def generate_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = create_email(first_name, last_name)
        username = create_username(first_name, last_name)
        type = choices(['admin', 'tutor', 'student'], weights=[3, 12, 85], k=1)[0]
        if type == 'tutor':
            subjects = choices(Subject.objects.all(), k=randint(1, 5))
        else:
            subjects = []
        self.create_user({'username': username, 'email': email, 'first_name': first_name, 'last_name': last_name, 'type': type, 'subjects': subjects})

    def create_user(self, data):
        try:
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=Command.DEFAULT_PASSWORD,
                first_name=data['first_name'],
                last_name=data['last_name'],
                type=data['type']
            )
            if data['type'] == 'tutor':
                user.subjects.set(data['subjects'])
            if data['type'] == 'admin':
                user.is_staff = True
                user.is_superuser = True
            user.save()
        except:
            pass


    # Lesson seeding
    def create_lessons(self):
        self.generate_lesson_fixtures()
        self.generate_random_lessons()

    def generate_lesson_fixtures(self):
        lesson_fixtures = [
            {'student': User.objects.get(username='@charlie'), 'subject': Subject.objects.get(name='Python'), 'tutor': User.objects.get(username='@janedoe'), 'date': datetime(2024, 8, 12, 10, 0, tzinfo=pytz.utc), 'duration': 45, 'status': 'Approved', 'recurrence': 'None', 'recurrence_end_date': None},
            {'student': User.objects.get(username='@charlie'), 'subject': Subject.objects.get(name='Java'), 'tutor': User.objects.get(username='@janedoe'), 'date': now()+timedelta(days=1), 'duration': 60, 'status': 'Pending', 'recurrence': 'None', 'recurrence_end_date': None},
            {'student': User.objects.get(username='@charlie'), 'subject': Subject.objects.get(name='C++'), 'tutor': User.objects.get(username='@janedoe'), 'date': now()+timedelta(days=1, hours=2), 'duration': 120, 'status': 'Approved', 'recurrence': 'Weekly', 'recurrence_end_date': now()+timedelta(days=50)},
        ]
        for data in lesson_fixtures:
            self.create_lesson(data)

    def generate_random_lessons(self):
        lesson_count = Lesson.objects.count()
        for user in User.objects.all():
            if user.type == 'student' and not Lesson.objects.filter(student=user).exists():
                for _ in range(randint(2, 10)):
                    print(f"Seeding lessons {lesson_count}", end='\r')
                    self.generate_lesson(user)
                    lesson_count = Lesson.objects.count()
        print("Lesson seeding complete.      ")
    
    def generate_lesson(self, user):
        student=user
        subject=choices(Subject.objects.all(), k=1)[0]
        tutor=choices(User.objects.filter(type='tutor'), k=1)[0]
        date = self.faker.date_time_between(start_date='-1y', end_date='+1y', tzinfo=pytz.utc)
        duration=randint(2, 16) * 15
        status = choices(['Pending', 'Approved', 'Rejected'], weights=[2, 1, 1], k=1)[0]
        recurrence = choices(['None', 'Daily', 'Weekly', 'Monthly'], weights=[80, 1, 10, 10], k=1)[0]
        if recurrence != 'None':
            recurrence_end_date = date + timedelta(days=randint(1, 365))
        else:
            recurrence_end_date = None
        self.create_lesson({'student': student, 'subject': subject, 'tutor': tutor, 'date': date, 'duration': duration, 'status': status, 'recurrence': recurrence, 'recurrence_end_date': recurrence_end_date})
    
    def create_lesson(self, data):
        try:
            Lesson.objects.create(
                student=data['student'],
                subject=data['subject'],
                tutor=data['tutor'],
                date=data['date'],
                duration=data['duration'],
                status=data['status'],
                recurrence=data['recurrence'],
                recurrence_end_date=data['recurrence_end_date'],
            )
        except:
            pass
    

    # Invoice seeding
    def create_invoices(self):
        self.generate_invoice_fixtures()
        self.generate_random_invoices()

    def generate_invoice_fixtures(self):
        invoice_fixtures = [
            {'student': User.objects.get(username='@charlie'), 'lesson': None, 'amount': 22.5, 'due_date': datetime(2024, 8, 22, 10, 0, tzinfo=pytz.utc), 'paid': False},
            {'student': User.objects.get(username='@charlie'), 'lesson': None, 'amount': 30, 'due_date': now()+timedelta(days=4), 'paid': True},
            {'student': User.objects.get(username='@charlie'), 'lesson': None, 'amount': 60, 'due_date': now()+timedelta(days=11, hours=2), 'paid': False},
        ]
        for data in invoice_fixtures:
            self.create_invoice(data)

    def generate_random_invoices(self):
        invoice_count = Invoice.objects.count()
        for lesson in Lesson.objects.all():
            if lesson.status == 'Approved' and not Invoice.objects.filter(lesson=lesson).exists():
                print(f"Seeding invoices {invoice_count}", end='\r')
                self.generate_invoice(lesson)
                invoice_count = Invoice.objects.count()
        print("Invoice seeding complete.      ")
    
    def generate_invoice(self, obj):
        student=obj.student
        lesson=obj
        amount=calculate_invoice_amount(obj)
        due_date=obj.date + timedelta(days=randint(-10, 20))
        paid=choices([True, False], weights=[1, 1], k=1)[0]
        self.create_invoice({'student': student, 'lesson': lesson, 'amount': amount, 'due_date': due_date, 'paid': paid})

    def create_invoice(self, data):
        try:
            Invoice.objects.create(
                student=data['student'],
                lesson=data['lesson'],
                amount=data['amount'],
                due_date=data['due_date'],
                paid=data['paid'],
            )
        except:
            pass


    # Notification seeding
    def create_notifications(self):
        self.generate_notification_fixtures()
        self.generate_random_notifications()
    
    def generate_notification_fixtures(self):
        notification_fixtures = [
            {'user': User.objects.get(username='@charlie'), 'message': 'You have a new lesson with Jane Doe on Python scheduled for tomorrow.', 'created_at': now()-timedelta(days=1), 'is_read': False},
            {'user': User.objects.get(username='@charlie'), 'message': 'Your invoice for lesson with Jane Doe on Python is due in 3 days.', 'created_at': now()-timedelta(days=2), 'is_read': True},
            {'user': User.objects.get(username='@janedoe'), 'message': 'Your invoice for lesson with Jane Doe on Python is overdue.', 'created_at': now()-timedelta(days=1, hours=2), 'is_read': False},
        ]
        for data in notification_fixtures:
            self.create_notification(data)
    
    def generate_random_notifications(self):
        notification_count = Notification.objects.count()
        for user in User.objects.all():
            if not Notification.objects.filter(user=user).exists():
                for _ in range(randint(1, 4)):
                    print(f"Seeding notification {notification_count}", end='\r')
                    self.generate_notification(user)
                    notification_count = Notification.objects.count()
        print("Notification seeding complete.      ")

    def generate_notification(self, user):
        user=user
        message=self.faker.sentence()
        created_at=self.faker.date_time_between(start_date='-1y', end_date='+1y', tzinfo=pytz.utc)
        is_read=choices([True, False], weights=[1, 1], k=1)[0]
        self.create_notification({'user': user, 'message': message, 'created_at': created_at, 'is_read': is_read})
    
    def create_notification(self, data):
        try:
            Notification.objects.create(
                user=data['user'],
                message=data['message'],
                created_at=data['created_at'],
                is_read=data['is_read'],
            )
        except:
            pass


def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    return first_name + '.' + last_name + '@example.org'

def days_between(start_date, end_date):
    return (end_date - start_date).days

def calculate_invoice_amount(lesson):
    if lesson is None:
        return randint(10, 200)
    if lesson.recurrence == 'None':
        repetitions = 1
    elif lesson.recurrence == 'Daily':
        repetitions = days_between(lesson.date, datetime.combine(lesson.recurrence_end_date, datetime.min.time(), tzinfo=pytz.utc))
    elif lesson.recurrence == 'Weekly':
        repetitions = days_between(lesson.date, datetime.combine(lesson.recurrence_end_date, datetime.min.time(), tzinfo=pytz.utc)) // 7
    elif lesson.recurrence == 'Monthly':
        repetitions = days_between(lesson.date, datetime.combine(lesson.recurrence_end_date, datetime.min.time(), tzinfo=pytz.utc)) // 30
    return lesson.duration * 0.5 * repetitions