from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Lesson, Subject
from django.utils import timezone
from datetime import timedelta

class SearchSortTest(TestCase):
    #tests for search and sort functionality

    def setUp(self):
        #create test subjects
        self.python = Subject.objects.create(name='Python')
        self.java = Subject.objects.create(name='Java')

        #create test users
        self.admin = User.objects.create_user(
            username='@adminuser',
            email='admin@test.com',
            password='Password123',
            first_name='Admin',
            last_name='User',
            type='admin'
        )

        self.student1 = User.objects.create_user(
            username='@student1',
            email='student1@test.com',
            password='Password123',
            first_name='Student',
            last_name='One',
            type='student'
        )

        self.student2 = User.objects.create_user(
            username='@student2',
            email='student2@test.com',
            password='Password123',
            first_name='Student',
            last_name='Two',
            type='student'
        )

        #create test lessons
        self.lesson1 = Lesson.objects.create(
            student=self.student1,
            subject=self.python,
            date=timezone.now() + timedelta(days=1),
            duration=60,
            status='Pending',
            recurrence='None',
            recurrence_end_date=None
        )

        self.lesson2 = Lesson.objects.create(
            student=self.student2,
            subject=self.java,
            date=timezone.now() + timedelta(days=2),
            duration=90,
            status='Approved',
            recurrence='None',
            recurrence_end_date=None
        )

        self.client.login(username='@adminuser', password='Password123')

    def test_lesson_search(self):
        #test searching lessons
        url = reverse('list_lessons')

        #test search by subject
        response = self.client.get(url, {'search': self.python.name})
        lessons = list(response.context['lessons'])  #convert to list to force query evaluation
        self.assertEqual(len(lessons), 1)
        self.assertEqual(lessons[0].subject, self.python)

        #test search by student username
        response = self.client.get(url, {'search': '@student1'})
        lessons = list(response.context['lessons'])
        self.assertEqual(len(lessons), 1)
        self.assertEqual(lessons[0].student.username, '@student1')

    def test_lesson_filtering(self):
        #test filtering lessons
        url = reverse('list_lessons')

        #test status filter
        response = self.client.get(url, {'status': 'Pending'})
        lessons = list(response.context['lessons'])
        self.assertEqual(len(lessons), 1)
        self.assertEqual(lessons[0].subject, self.python)

    def test_lesson_sorting(self):
        #test sorting lessons
        url = reverse('list_lessons')

        #test sort by date ascending
        response = self.client.get(url, {'order_by': 'date'})
        lessons = response.context['lessons']
        self.assertEqual(lessons[0], self.lesson1)
        self.assertEqual(lessons[1], self.lesson2)

        #test sort by date descending
        response = self.client.get(url, {'order_by': '-date'})
        lessons = response.context['lessons']
        self.assertEqual(lessons[0], self.lesson2)
        self.assertEqual(lessons[1], self.lesson1)

        #test sort by subject
        response = self.client.get(url, {'order_by': 'subject__name'})
        lessons = response.context['lessons']
        self.assertEqual(lessons[0], self.lesson2)
        self.assertEqual(lessons[1], self.lesson1)

    def test_multiple_filters(self):
        #test combining multiple filters
        url = reverse('list_lessons')

        #test combining status and duration filters
        response = self.client.get(url, {
            'status': 'Pending',
            'duration': '60'
        })
        lessons = list(response.context['lessons'])
        self.assertEqual(len(lessons), 1)
        self.assertEqual(lessons[0].subject, self.python)
