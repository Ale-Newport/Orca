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
    #base test case to be used for all selenium tests

    def setUp(self):
        #initialize browser and set implicit wait
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(10)
        self.wait = WebDriverWait(self.browser, 10)

        #create test users
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
        #close the browser after each test
        self.browser.quit()

    def login(self, user):
        #helper method to log in a user
        self.browser.get(f'{self.live_server_url}{reverse("log_in")}')

        #find and fill username field
        username_field = self.browser.find_element(By.NAME, 'username')
        username_field.send_keys(user.username)

        #find and fill password field
        password_field = self.browser.find_element(By.NAME, 'password')
        password_field.send_keys('Password123')

        #submit the form
        password_field.submit()

        #wait for redirect to complete
        try:
            self.wait.until(
                lambda driver: driver.current_url != f'{self.live_server_url}{reverse("log_in")}'
            )
        except TimeoutException:
            self.fail("login timeout - redirect did not occur")

    def wait_for_element(self, by, value, timeout=10):
        #helper method to wait for an element to be present
        try:
            element = WebDriverWait(self.browser, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            self.fail(f"element {value} not found within {timeout} seconds")

    def wait_for_text(self, text, timeout=10):
        #helper method to wait for text to be present on the page
        try:
            WebDriverWait(self.browser, timeout).until(
                EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{text}')]"))
            )
        except TimeoutException:
            self.fail(f"text '{text}' not found within {timeout} seconds")