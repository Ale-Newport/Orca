from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Lesson
from django.utils import timezone
from datetime import timedelta

class SearchSortTest(TestCase):
    """Tests for search and sort functionality."""
    
    def setUp(self):
        # Create test users
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
        
        # Create test lessons
        self.lesson1 = Lesson.objects.create(
            student=self.student1,
            subject='Python',
            date=timezone.now() + timedelta(days=1),
            duration=60,
            status='Pending'
        )
        
        self.lesson2 = Lesson.objects.create(
            student=self.student2,
            subject='Java',
            date=timezone.now() + timedelta(days=2),
            duration=90,
            status='Approved'
        )
        
        self.client.login(username='@adminuser', password='Password123')

    def test_lesson_search(self):
        """Test searching lessons."""
        url = reverse('list_lessons')
        
        # Test search by subject
        response = self.client.get(url, {'search': 'Python'})
        lessons = list(response.context['lessons'])  # Convert to list to force query evaluation
        self.assertEqual(len(lessons), 1)
        self.assertEqual(lessons[0].subject, 'Python')
        
        # Test search by student username
        response = self.client.get(url, {'search': '@student1'})
        lessons = list(response.context['lessons'])
        self.assertEqual(len(lessons), 1)
        self.assertEqual(lessons[0].student.username, '@student1')

    def test_lesson_filtering(self):
        """Test filtering lessons."""
        url = reverse('list_lessons')
        
        # Test status filter
        response = self.client.get(url, {'status': 'Pending'})
        lessons = list(response.context['lessons'])
        self.assertEqual(len(lessons), 1)
        self.assertEqual(lessons[0].subject, 'Python')

    def test_lesson_sorting(self):
        """Test sorting lessons."""
        url = reverse('list_lessons')
        
        # Test sort by date ascending
        response = self.client.get(url, {'order_by': 'date'})
        lessons = response.context['lessons']
        self.assertEqual(lessons[0], self.lesson1)
        self.assertEqual(lessons[1], self.lesson2)
        
        # Test sort by date descending
        response = self.client.get(url, {'order_by': '-date'})
        lessons = response.context['lessons']
        self.assertEqual(lessons[0], self.lesson2)
        self.assertEqual(lessons[1], self.lesson1)
        
        # Test sort by subject
        response = self.client.get(url, {'order_by': 'subject'})
        lessons = response.context['lessons']
        self.assertEqual(lessons[0], self.lesson2)  # Java comes before Python
        self.assertEqual(lessons[1], self.lesson1)

    def test_multiple_filters(self):
        """Test combining multiple filters."""
        url = reverse('list_lessons')
        
        # Test combining status and duration filters
        response = self.client.get(url, {
            'status': 'Pending',
            'duration': '60'
        })
        lessons = list(response.context['lessons'])
        self.assertEqual(len(lessons), 1)
        self.assertEqual(lessons[0].subject, 'Python')