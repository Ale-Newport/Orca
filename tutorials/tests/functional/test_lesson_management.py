from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from ..functional.test_selenium import SeleniumTestCase

class ProfileManagementTest(SeleniumTestCase):
    def setUp(self):
        super().setUp()
        self.login(self.student)

    def find_submit_button(self):
        """Helper method to find submit button regardless of type."""
        try:
            # Try to find button first
            return self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        except:
            try:
                # Try to find input submit next
                return self.browser.find_element(By.CSS_SELECTOR, 'input[type="submit"]')
            except:
                # Try to find any submit element
                return self.browser.find_element(By.CSS_SELECTOR, '[type="submit"]')

    def test_profile_update(self):
        """Test profile information update."""
        self.browser.get(f'{self.live_server_url}{reverse("profile")}')
        
        # Update first name
        first_name_input = self.browser.find_element(By.NAME, 'first_name')
        first_name_input.clear()
        first_name_input.send_keys('UpdatedName')
        
        # Submit form using any available submit element
        submit_button = self.find_submit_button()
        submit_button.click()
        
        # Wait for redirect to dashboard
        WebDriverWait(self.browser, 10).until(
            EC.url_contains('dashboard')
        )

        # Verify the update was successful
        self.browser.get(f'{self.live_server_url}{reverse("profile")}')
        updated_name = self.browser.find_element(By.NAME, 'first_name').get_attribute('value')
        self.assertEqual(updated_name, 'UpdatedName')

    def test_password_change(self):
        """Test password change functionality."""
        self.browser.get(f'{self.live_server_url}{reverse("password")}')
        
        # Fill out password change form
        old_password = self.browser.find_element(By.NAME, 'password')
        new_password = self.browser.find_element(By.NAME, 'new_password')
        password_confirmation = self.browser.find_element(By.NAME, 'password_confirmation')
        
        old_password.send_keys('Password123')
        new_password.send_keys('NewPassword123')
        password_confirmation.send_keys('NewPassword123')
        
        # Submit form using any available submit element
        submit_button = self.find_submit_button()
        submit_button.click()
        
        # Wait for redirect to dashboard
        WebDriverWait(self.browser, 10).until(
            EC.url_contains('dashboard')
        )

        # Verify the password change was successful by logging in with new password
        self.browser.get(f'{self.live_server_url}{reverse("log_out")}')
        self.browser.get(f'{self.live_server_url}{reverse("log_in")}')
        
        username_field = self.browser.find_element(By.NAME, 'username')
        password_field = self.browser.find_element(By.NAME, 'password')
        
        username_field.send_keys(self.student.username)
        password_field.send_keys('NewPassword123')
        
        submit_button = self.find_submit_button()
        submit_button.click()
        
        # Wait for successful login redirect
        WebDriverWait(self.browser, 10).until(
            EC.url_contains('dashboard')
        )

    def test_notifications_page(self):
        """Test notifications page functionality."""
        self.browser.get(f'{self.live_server_url}{reverse("notifications")}')
        
        # Wait for page load
        self.wait_for_element(By.CLASS_NAME, 'container')
        
        # Verify we can access the page
        current_url = self.browser.current_url
        expected_url = f'{self.live_server_url}{reverse("notifications")}'
        self.assertEqual(current_url, expected_url)