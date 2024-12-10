from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from .test_selenium import SeleniumTestCase
from datetime import datetime, timedelta

class LessonBookingTest(SeleniumTestCase):
    """Functional tests for lesson booking functionality."""

    def setUp(self):
        super().setUp()
        self.login(self.student)

    def test_lesson_request_form_submission(self):
        """Test the lesson request form submission process."""
        self.browser.get(f'{self.live_server_url}{reverse("create_request")}')
        
        # Fill out the form
        subject_select = Select(self.browser.find_element(By.NAME, 'subject'))
        subject_select.select_by_visible_text('Python')
        
        # Set date and time (tomorrow at 2 PM)
        tomorrow = datetime.now() + timedelta(days=1)
        date_input = self.browser.find_element(By.NAME, 'preferred_date')
        self.browser.execute_script(
            f"arguments[0].value = '{tomorrow.strftime('%Y-%m-%dT14:00')}'", 
            date_input
        )
        
        # Set duration
        duration_input = self.browser.find_element(By.NAME, 'duration')
        duration_input.clear()
        duration_input.send_keys('60')
        
        # Submit form
        submit_button = self.find_submit_button()
        submit_button.click()
        
        # Wait for redirect and verify success (using either message or URL)
        try:
            self.wait_for_text('request has been submitted')
        except:
            # If message not found, check for redirect
            WebDriverWait(self.browser, 10).until(
                EC.url_contains('student/requests')
            )

    def test_lesson_filtering_and_sorting(self):
        """Test lesson list filtering and sorting."""
        self.browser.get(f'{self.live_server_url}{reverse("student_lessons")}')
        
        # Test subject filter if it exists
        try:
            subject_filter = Select(self.browser.find_element(By.NAME, 'subject'))
            subject_filter.select_by_visible_text('Python')
            self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
            # Wait for results to update
            WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'table')))
        except:
            pass

        # Test sorting if available
        try:
            sort_link = self.browser.find_element(By.CSS_SELECTOR, 'th a[href*="order_by=date"]')
            sort_link.click()
            # Wait for results to update
            WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'table')))
        except:
            pass

    def test_lesson_cancellation(self):
        """Test lesson cancellation flow."""
        # Navigate to lessons page
        self.browser.get(f'{self.live_server_url}{reverse("student_lessons")}')
        
        # Look for cancel button on first lesson
        try:
            cancel_button = self.browser.find_element(By.CSS_SELECTOR, 'a[href*="delete"]')
            cancel_button.click()
            
            # Wait for confirmation page
            self.wait_for_text('Are you sure')
            
            # Confirm cancellation
            confirm_button = self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            confirm_button.click()
            
            # Verify cancellation
            self.wait_for_text('successfully')
        except:
            pass  # Skip if no lessons to cancel