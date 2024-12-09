from django.test import TestCase
from tutorials.models import Subject

class SubjectModelTest(TestCase):
    """Tests for the Subject model validation."""

    def test_valid_subject_names(self):
        """Test that valid subject names are accepted."""
        valid_subjects = ['Python', 'Java', 'C++', 'Web Development', 'Scala']
        for subject_name in valid_subjects:
            subject = Subject(name=subject_name)
            try:
                subject.full_clean()
                self.assertTrue(True)  # Should reach this point
            except:
                self.fail(f"Subject {subject_name} should be valid")

    def test_subject_string_representation(self):
        """Test the string representation of subjects."""
        subject = Subject(name='Python')
        self.assertEqual(str(subject), 'Python')


    def test_subject_case_sensitivity(self):
        """Test that subject names are case-sensitive."""
        Subject.objects.create(name='Python')
        python_count = Subject.objects.filter(name='Python').count()
        PYTHON_count = Subject.objects.filter(name='PYTHON').count()
        self.assertEqual(python_count, 1)
        self.assertEqual(PYTHON_count, 0)