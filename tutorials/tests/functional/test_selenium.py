from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from tutorials.models import User
import time

class SeleniumTestCase(StaticLiveServerTestCase):
    """Base test case to be used for all Selenium tests."""
    
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(10)
        self.wait = WebDriverWait(self.browser, 10)
        
        # Create test users
        self.student = User.objects.create_user(
            username='@testStudent',
            email='student@test.com',
            password='Password123',
            first_name='Test',
            last_name='Student',
            type='student'
        )
        
        self.tutor = User.objects.create_user(
            username='@testTutor',
            email='tutor@test.com',
            password='Password123',
            first_name='Test',
            last_name='Tutor',
            type='tutor'
        )
        
        self.admin = User.objects.create_user(
            username='@testAdmin',
            email='admin@test.com',
            password='Password123',
            first_name='Test',
            last_name='Admin',
            type='admin'
        )

    def tearDown(self):
        self.browser.quit()

    def login(self, user):
        """Helper method to log in a user."""
        self.browser.get(f'{self.live_server_url}{reverse("log_in")}')
        
        # Find and fill username field
        username_field = self.browser.find_element(By.NAME, 'username')
        username_field.send_keys(user.username)
        
        # Find and fill password field
        password_field = self.browser.find_element(By.NAME, 'password')
        password_field.send_keys('Password123')
        
        # Submit the form
        password_field.submit()
        
        # Wait for redirect to complete
        try:
            self.wait.until(
                lambda driver: driver.current_url != f'{self.live_server_url}{reverse("log_in")}'
            )
        except TimeoutException:
            self.fail("Login timeout - redirect did not occur")

    def wait_for_element(self, by, value, timeout=10):
        """Helper method to wait for an element to be present."""
        try:
            element = WebDriverWait(self.browser, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            self.fail(f"Element {value} not found within {timeout} seconds")

    def wait_for_text(self, text, timeout=10):
        """Helper method to wait for text to be present on the page."""
        try:
            WebDriverWait(self.browser, timeout).until(
                EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{text}')]"))
            )
        except TimeoutException:
            self.fail(f"Text '{text}' not found within {timeout} seconds")