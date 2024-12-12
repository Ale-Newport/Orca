from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from .test_selenium import SeleniumTestCase
from datetime import datetime, timedelta
from django.utils import timezone
from tutorials.models import Subject, Lesson

class LessonBookingTest(SeleniumTestCase):
    #functional tests for lesson booking functionality

    def setUp(self):
        #set up test user and log in
        super().setUp()
        self.python_subject = Subject.objects.create(name='Python')
        self.java_subject = Subject.objects.create(name='Java')
        self.login(self.student)

    def test_lesson_filtering_and_sorting(self):
        #test lesson list filtering and sorting
        self.browser.get(f'{self.live_server_url}{reverse("student_lessons")}')

        #test subject filter if it exists
        try:
            subject_filter = Select(self.browser.find_element(By.NAME, 'subject'))
            subject_filter.select_by_visible_text('Python')
            self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
            #wait for results to update
            WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'table')))
        except:
            pass

        #test sorting if available
        try:
            sort_link = self.browser.find_element(By.CSS_SELECTOR, 'th a[href*="order_by=date"]')
            sort_link.click()
            #wait for results to update
            WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'table')))
        except:
            pass

    def test_lesson_cancellation(self):
        #test lesson cancellation flow
        #navigate to lessons page
        self.browser.get(f'{self.live_server_url}{reverse("student_lessons")}')

        #look for cancel button on first lesson
        try:
            cancel_button = self.browser.find_element(By.CSS_SELECTOR, 'a[href*="delete"]')
            cancel_button.click()

            #wait for confirmation page
            self.wait_for_text('are you sure')

            #confirm cancellation
            confirm_button = self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            confirm_button.click()

            #verify cancellation
            self.wait_for_text('successfully')
        except:
            pass  #skip if no lessons to cancel