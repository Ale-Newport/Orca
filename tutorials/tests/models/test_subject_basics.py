from django.test import TestCase
from django.db import IntegrityError
from tutorials.models import Subject

class SubjectBasicsTest(TestCase):
    def test_create_python_subject(self):
        subject = Subject.objects.create(name='Python')
        self.assertEqual(subject.name, 'Python')

    def test_create_java_subject(self):
        subject = Subject.objects.create(name='Java')
        self.assertEqual(subject.name, 'Java')

    def test_subject_choices_include_python(self):
        self.assertIn(('Python', 'Python'), Subject._meta.get_field('name').choices)

    def test_subject_choices_include_java(self):
        self.assertIn(('Java', 'Java'), Subject._meta.get_field('name').choices)

    def test_subject_choices_include_web_development(self):
        self.assertIn(('Web Development', 'Web Development'), Subject._meta.get_field('name').choices)

    def test_subject_uniqueness(self):
        Subject.objects.create(name='Python')
        with self.assertRaises(IntegrityError):
            Subject.objects.create(name='Python')