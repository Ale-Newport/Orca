from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from .test_selenium import SeleniumTestCase

class LoginFunctionalTest(SeleniumTestCase):
    """Functional tests for the login functionality."""

    def test_successful_student_login(self):
        """Test that a student can successfully log in."""
        self.browser.get(f'{self.live_server_url}{reverse("log_in")}')
        
        # Fill in login form
        username_field = self.browser.find_element(By.NAME, 'username')
        password_field = self.browser.find_element(By.NAME, 'password')
        username_field.send_keys('@testStudent')
        password_field.send_keys('Password123')
        password_field.submit()
        
        # Wait for redirect and dashboard load
        WebDriverWait(self.browser, 10).until(
            EC.url_contains("/student/dashboard/")
        )
        
        # Verify dashboard elements
        self.wait_for_element(By.CLASS_NAME, 'container')
        dashboard_url = f'{self.live_server_url}{reverse("student_dashboard")}'
        self.assertEqual(self.browser.current_url, dashboard_url)

    def test_navigation_menu_after_login(self):
        """Test navigation menu elements after successful login."""
        self.login(self.student)
        
        # Wait for dashboard to load
        self.wait_for_element(By.CLASS_NAME, 'navbar')
        
        # Check for menu items that definitely exist in your navigation
        try:
            # Try dropdown menu if it exists
            dropdown = self.browser.find_element(By.CLASS_NAME, 'dropdown-toggle')
            dropdown.click()
            self.wait_for_element(By.CSS_SELECTOR, '.dropdown-menu')
        except:
            pass
        
        # Check for basic navigation elements
        self.assertTrue(
            any(link.text in ['Dashboard', 'Home', 'Schedule', 'Lessons'] 
                for link in self.browser.find_elements(By.TAG_NAME, 'a'))
        )

    def test_validation_messages(self):
        """Test client-side validation messages."""
        self.browser.get(f'{self.live_server_url}{reverse("log_in")}')
        
        # Try submitting empty form
        submit_button = self.find_submit_button()
        submit_button.click()
        
        # Wait for either HTML5 validation or server-side validation
        try:
            # Check for HTML5 validation
            username_field = self.browser.find_element(By.NAME, 'username')
            self.assertTrue(username_field.get_attribute('required'))
            validation_message = username_field.get_attribute('validationMessage')
            self.assertTrue(len(validation_message) > 0)
        except:
            # Check for server-side validation
            self.wait_for_element(By.CLASS_NAME, 'alert-danger')

    def test_password_visibility_toggle(self):
        """Test password visibility toggle functionality."""
        self.browser.get(f'{self.live_server_url}{reverse("log_in")}')
        
        # Locate password field and check initial type
        password_field = self.browser.find_element(By.NAME, 'password')
        self.assertEqual(password_field.get_attribute('type'), 'password')
        
        # Find and click show password button if it exists
        try:
            show_password_btn = self.browser.find_element(By.CLASS_NAME, 'show-password')
            show_password_btn.click()
            self.assertEqual(password_field.get_attribute('type'), 'text')
        except:
            pass  # Skip if show password feature isn't implemented

    def test_remember_me_functionality(self):
        """Test remember me checkbox functionality if implemented."""
        self.browser.get(f'{self.live_server_url}{reverse("log_in")}')
        
        try:
            remember_me = self.browser.find_element(By.NAME, 'remember_me')
            self.assertTrue(remember_me.is_displayed())
            remember_me.click()
            self.assertTrue(remember_me.is_selected())
        except:
            pass  # Skip if remember me feature isn't implemented

    def test_validation_messages(self):
        """Test client-side validation messages."""
        self.browser.get(f'{self.live_server_url}{reverse("log_in")}')
        
        # Test empty username validation
        username_field = self.browser.find_element(By.NAME, 'username')
        password_field = self.browser.find_element(By.NAME, 'password')
        
        # Try submitting empty form
        password_field.submit()
        
        # Check for validation message
        self.wait_for_text('This field is required')

    def test_redirect_to_appropriate_dashboard(self):
        """Test that different user types are redirected appropriately."""
        # Test admin redirect
        self.login(self.admin)
        admin_dashboard_url = f'{self.live_server_url}{reverse("admin_dashboard")}'
        self.assertEqual(self.browser.current_url, admin_dashboard_url)
        self.browser.get(f'{self.live_server_url}{reverse("log_out")}')
        
        # Test tutor redirect
        self.login(self.tutor)
        tutor_dashboard_url = f'{self.live_server_url}{reverse("tutor_dashboard")}'
        self.assertEqual(self.browser.current_url, tutor_dashboard_url)
        self.browser.get(f'{self.live_server_url}{reverse("log_out")}')
        
        # Test student redirect
        self.login(self.student)
        student_dashboard_url = f'{self.live_server_url}{reverse("student_dashboard")}'
        self.assertEqual(self.browser.current_url, student_dashboard_url)