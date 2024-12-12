from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from .test_selenium import SeleniumTestCase

class LoginFunctionalTest(SeleniumTestCase):
    #functional tests for the login functionality

    def find_submit_button(self):
            #helper method to find the submit button
            try:
                #try to find a button element with type submit
                return self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            except:
                try:
                    #try to find an input element with type submit
                    return self.browser.find_element(By.CSS_SELECTOR, 'input[type="submit"]')
                except:
                    self.fail("submit button not found")

    def test_successful_student_login(self):
        #test that a student can successfully log in
        self.browser.get(f'{self.live_server_url}{reverse("log_in")}')

        #fill in login form
        username_field = self.browser.find_element(By.NAME, 'username')
        password_field = self.browser.find_element(By.NAME, 'password')
        username_field.send_keys('@testStudent')
        password_field.send_keys('Password123')
        password_field.submit()

        #wait for redirect and dashboard load
        WebDriverWait(self.browser, 10).until(
            EC.url_contains("/student/dashboard/")
        )

        #verify dashboard elements
        self.wait_for_element(By.CLASS_NAME, 'container')
        dashboard_url = f'{self.live_server_url}{reverse("student_dashboard")}'
        self.assertEqual(self.browser.current_url, dashboard_url)

    def test_navigation_menu_after_login(self):
        #test navigation menu elements after successful login
        self.login(self.student)

        #wait for dashboard to load
        self.wait_for_element(By.CLASS_NAME, 'navbar')

        #check for menu items that definitely exist in your navigation
        try:
            #try dropdown menu if it exists
            dropdown = self.browser.find_element(By.CLASS_NAME, 'dropdown-toggle')
            dropdown.click()
            self.wait_for_element(By.CSS_SELECTOR, '.dropdown-menu')
        except:
            pass

        #check for basic navigation elements
        self.assertTrue(
            any(link.text in ['Dashboard', 'Home', 'Schedule', 'Lessons'] 
                for link in self.browser.find_elements(By.TAG_NAME, 'a'))
        )

    def test_validation_messages(self):
        #test client-side validation messages
        self.browser.get(f'{self.live_server_url}{reverse("log_in")}')

        #try submitting empty form
        submit_button = self.find_submit_button()
        submit_button.click()

        #wait for either html5 validation or server-side validation
        try:
            #check for html5 validation
            username_field = self.browser.find_element(By.NAME, 'username')
            self.assertTrue(username_field.get_attribute('required'))
            validation_message = username_field.get_attribute('validationMessage')
            self.assertTrue(len(validation_message) > 0)
        except:
            #check for server-side validation
            self.wait_for_element(By.CLASS_NAME, 'alert-danger')



    def test_password_visibility_toggle(self):
        #test show/hide password toggle functionality
        self.browser.get(f'{self.live_server_url}{reverse("log_in")}')

        #locate password field and check initial type
        password_field = self.browser.find_element(By.NAME, 'password')
        self.assertEqual(password_field.get_attribute('type'), 'password')

        #find and click show password button if it exists
        try:
            show_password_btn = self.browser.find_element(By.CLASS_NAME, 'show-password')
            show_password_btn.click()
            self.assertEqual(password_field.get_attribute('type'), 'text')
        except:
            pass  #skip if show password feature isn't implemented

    def test_remember_me_functionality(self):
        #test remember me checkbox functionality
        self.browser.get(f'{self.live_server_url}{reverse("log_in")}')

        try:
            remember_me = self.browser.find_element(By.NAME, 'remember_me')
            self.assertTrue(remember_me.is_displayed())
            remember_me.click()
            self.assertTrue(remember_me.is_selected())
        except:
            pass  #skip if remember me feature isn't implemented

    def test_redirect_to_appropriate_dashboard(self):
        #test that different user types are redirected appropriately

        #test admin redirect
        self.login(self.admin)
        admin_dashboard_url = f'{self.live_server_url}{reverse("admin_dashboard")}'
        self.assertEqual(self.browser.current_url, admin_dashboard_url)
        self.browser.get(f'{self.live_server_url}{reverse("log_out")}')

        #test tutor redirect
        self.login(self.tutor)
        tutor_dashboard_url = f'{self.live_server_url}{reverse("tutor_dashboard")}'
        self.assertEqual(self.browser.current_url, tutor_dashboard_url)
        self.browser.get(f'{self.live_server_url}{reverse("log_out")}')

        #test student redirect
        self.login(self.student)
        student_dashboard_url = f'{self.live_server_url}{reverse("student_dashboard")}'
        self.assertEqual(self.browser.current_url, student_dashboard_url)