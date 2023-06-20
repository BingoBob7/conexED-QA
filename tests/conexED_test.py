# pytest -s shows print statements
# pytest -s --html=reports/report.html --self-contained-html tests

# pytest -s --alluredir=reports/my_allure_results tests
# allure serve reports/my_allure_results

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException,ElementNotInteractableException,NoSuchElementException
import time
import names
import string
import random
import json
import os



class TestRegistration:
    service = Service()
    driver = webdriver.Chrome(service=service)
    WAIT = WebDriverWait(driver,6)
    tabs = {}
    user_data = {}

    def resource_path(self,relative_path):
        base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def generate_password(self):
        letters = string.ascii_letters
        numbers = string.digits
        symbols = "!#$%&()*+"
        password = "".join(random.choice(letters) for i in range(10))
        password = password.join(random.choice(numbers) for i in range(2))
        password = password.join(random.choice(symbols) for i in range(2))
        return password

    def test_1_generate_user(self):
        first_name = names.get_first_name()
        last_name = names.get_last_name()
        domain = "dayrep.com"
        email = f'{first_name}{last_name}@{domain}'
        password = self.generate_password()
        user_data = {f"{first_name}{last_name}": {
            "firstname": first_name,
            "lastname": last_name,
            "username": f"{first_name}{last_name}",
            "domain": domain,
            "email": email,
            "password": password,
            "registered": False
        }}
        try:
            with open(self.resource_path("tests/user_data.json"), mode="r") as data_file:
                data = json.load(data_file)
        except FileNotFoundError:
                with open(self.resource_path("tests/user_data.json"), mode="w") as data_file:
                    json.dump(user_data, data_file, indent=4)
        else:
            data.update(user_data) # update will append the new data to the existing data
            with open(self.resource_path("tests/user_data.json"), mode="w") as data_file:
                json.dump(data, data_file, indent=4)
        return user_data[f"{first_name}{last_name}"]
    
    def test_2_get_user_data(self):
        global user_data
        with open(self.resource_path("tests/user_data.json"), mode="r") as data_file:
            data = json.load(data_file)
        for user in data:
            if data[user]['registered'] == False:
                user_data = data[user]
                break

    def test_3_activate_temp_mailbox(self):
        global user_data
        email_parts = user_data["email"].split("@")
        username = email_parts[0]
        domain = email_parts[1]
        self.tab_switcher("tempmailbox_tab",f"https://www.fakemailgenerator.com/#/{domain}/{username}")

    def tab_switcher(self,tab_name,url):
        if len(self.tabs) == 0:
            self.driver.get(url)
            self.tabs[tab_name] = self.driver.current_window_handle
        elif tab_name not in self.tabs:
            self.driver.switch_to.new_window("tab")
            self.tabs[tab_name] = self.driver.current_window_handle
            self.driver.get(url)
        else:
            self.driver.switch_to.window(self.tabs[tab_name])

    def test_4_go_to_conexed(self):
        self.tab_switcher("conexed_main_tab","https://my.test.craniumcafe.com")

    def test_5_search_for_school(self):
        school_input_locator = (By.ID,'school-search')
        school_input = self.WAIT.until(EC.visibility_of_element_located(school_input_locator))
        try:
            school_input.send_keys("c")
        except ElementNotInteractableException:
            raise ElementNotInteractableException("School input is not interactable. There is likely an alert or modal blocking it.")
        school_list_locator = (By.CSS_SELECTOR, 'ul[id^="ui-id"]')
        school_list = self.WAIT.until(EC.visibility_of_element_located(school_list_locator))
        try:
            school_item = school_list.find_element(By.XPATH,'//li[text()="Cranium Cafe - Test"]')
            # school_item = school_list.find_element(By.XPATH,'//li[text()="dingdong"]')
        except NoSuchElementException:
            raise NoSuchElementException("School not found in list")
        school_item.click()

    def test_6_confirm_login_redirect(self):
        confirm_btn_locator = (By.ID,"integration-redirect-button")
        confirm_btn = self.WAIT.until(EC.element_to_be_clickable(confirm_btn_locator))
        confirm_btn.click()
        self.driver.close()
        del self.tabs["conexed_main_tab"]

    def test_7_redirect_new_tab_handler(self):
        all_tabs = self.driver.window_handles
        for tab in all_tabs:
            if tab not in self.tabs.values():
                self.driver.switch_to.window(tab)
                self.tabs[self.driver.title] = tab
        return self.driver.title

    def test_8_switch_to_first_iframe(self):
        self.driver.switch_to.frame(0)

    def test_9_choose_guest_registration(self):
        login_method_btn = self.driver.find_element(By.CSS_SELECTOR,"button#craniumcafe-button")
        login_method_btn.click()
        # TODO assert modal loads
        register_toggle_button = self.driver.find_element(By.ID,"register-toggle-button")
        register_toggle_button.click()

    def test_10_fill_out_registration_form(self):
        with open(self.resource_path("tests/user_data.json"), mode="r") as data_file:
            data = json.load(data_file)
        for user in data:
            if data[user]['registered'] == False:
                first_name = data[user]['firstname']
                last_name = data[user]['lastname']
                email = data[user]['email']
                password = data[user]['password']
                break
        fullname_entry_locator = (By.ID,"fullname-text")
        fullname_entry = self.WAIT.until(EC.visibility_of_element_located(fullname_entry_locator))
        fullname_entry.send_keys(f'{first_name} {last_name}')
        email_entry = self.driver.find_element(By.ID,"email-text")
        email_entry.send_keys(email)
        email_entry_locator = (By.CSS_SELECTOR,".login-input-wrapper:nth-child(2)")
        try:
            self.WAIT.until(EC.text_to_be_present_in_element_attribute(email_entry_locator, "class", "successed"))
        except TimeoutException:
            raise TimeoutException("Email entry took longer than 6 seconds to be visable.")
        create_password_entry = self.driver.find_element(By.ID,"create-password-text")
        create_password_entry.send_keys(password)
        confirm_password_entry = self.driver.find_element(By.ID,"confirm-password-text")
        confirm_password_entry.send_keys(password)
        # TODO assert form validations

    def test_11_submit_registration_form(self):
        register_btn = self.driver.find_element(By.ID,'register-button')
        register_btn.click()
        self.driver.close()
        del self.tabs["Login to ConexED"]

    def test_12_confirm_registration(self):
        # This test is heavily relient on fakemailgenerator.com which is a little janky. 
        # Any failures are likely to be do to that.
        global user_data
        self.tab_switcher("tempmailbox_tab",f"https://www.fakemailgenerator.com/#/{user_data['domain']}/{user_data['username']}")
        email_frame_locator = (By.ID,"emailFrame")
        try:
            email_frame = WebDriverWait(self.driver,60).until(EC.visibility_of_element_located(email_frame_locator))
        except TimeoutException:
            raise TimeoutException("Email took longer than 60 seconds to arrive")
        else:
            time.sleep(1)
            self.driver.execute_script("window.scrollBy(0,800)")
            time.sleep(1)
            self.driver.switch_to.frame(email_frame)
            register_link_locator = (By.XPATH,'//a[contains(text(),"https://cc.test.craniumcafe.com/register/")]')
            try:
                register_link = WebDriverWait(self.driver,15).until(EC.element_to_be_clickable(register_link_locator))
            except TimeoutException:
                raise TimeoutException("Register link took longer than 15 seconds to be clickable. This is an issue with FakeMailGenerator.")
            else:
                register_link.click()
                self.test_7_redirect_new_tab_handler()
                # TODO assert "Thank you for registering!"

                # TODO test the Return to sign in button
                # self.tab_switcher("Login to ConexED","https://cc.test.craniumcafe.com/login")
                # try:
                #     return_to_sign_in_btn = self.driver.find_element(By.LINK_TEXT,"Return to sign in")
                #     return_to_sign_in_btn.click()
                # except:
                #     pass



class TestLogin:
    service = Service()
    driver = webdriver.Chrome(service=service)
    WAIT = WebDriverWait(driver,6)
    tabs = {}
    user_data = {}

    def resource_path(self,relative_path):
        base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def test_1_get_user_data(self):
        global user_data
        with open(self.resource_path("tests/user_data.json"), mode="r") as data_file:
            data = json.load(data_file)
        for user in data:
            if data[user]['registered'] == False:
                user_data = data[user]
                break

    def tab_switcher(self,tab_name,url):
        if len(self.tabs) == 0:
            self.driver.get(url)
            self.tabs[tab_name] = self.driver.current_window_handle
        elif tab_name not in self.tabs:
            self.driver.switch_to.new_window("tab")
            self.tabs[tab_name] = self.driver.current_window_handle
            self.driver.get(url)
        else:
            self.driver.switch_to.window(self.tabs[tab_name]) 

    def test_2_go_to_conexed(self):
        self.tab_switcher("conexed_main_tab","https://my.test.craniumcafe.com")

    def test_3_search_for_school(self):
        school_input_locator = (By.ID,'school-search')
        school_input = self.WAIT.until(EC.visibility_of_element_located(school_input_locator))
        try:
            school_input.send_keys("c")
        except ElementNotInteractableException:
            raise ElementNotInteractableException("School input is not interactable. There is likely an alert or modal blocking it.")
        school_list_locator = (By.CSS_SELECTOR, 'ul[id^="ui-id"]')
        school_list = self.WAIT.until(EC.visibility_of_element_located(school_list_locator))
        try:
            school_item = school_list.find_element(By.XPATH,'//li[text()="Cranium Cafe - Test"]')
            # school_item = school_list.find_element(By.XPATH,'//li[text()="dingdong"]')
        except NoSuchElementException:
            raise NoSuchElementException("School not found in list")
        school_item.click()

    def test_4_confirm_login_redirect(self):
        confirm_btn_locator = (By.ID,"integration-redirect-button")
        confirm_btn = self.WAIT.until(EC.element_to_be_clickable(confirm_btn_locator))
        confirm_btn.click()
        self.driver.close()
        del self.tabs["conexed_main_tab"]

    def test_5_redirect_new_tab_handler(self):
        all_tabs = self.driver.window_handles
        for tab in all_tabs:
            if tab not in self.tabs.values():
                self.driver.switch_to.window(tab)
                self.tabs[self.driver.title] = tab
        return self.driver.title

    def test_6_switch_to_first_iframe(self):
        self.driver.switch_to.frame(0)

    def test_7_choose_guest_login(self):
        login_method_btn = self.driver.find_element(By.CSS_SELECTOR,"button#craniumcafe-button")
        login_method_btn.click()

    def test_8_enter_login_credentials(self):
        with open(self.resource_path("tests/user_data.json"), mode="r") as data_file:
            data = json.load(data_file)
        for user in data:
            if data[user]['registered'] == False:
                email = data[user]['email']
                password = data[user]['password']
                break
        login_entry = self.driver.find_element(By.ID,"login-text")
        login_entry.send_keys(email)
        password_entry = self.driver.find_element(By.ID,"password-text")
        password_entry.send_keys(password)

    def test_9_submit_login(self):
        login_btn = self.driver.find_element(By.ID,"login-button")
        login_btn.click()

    def test_10_confirm_logged_in(self):
        global user_data
        logged_in_user_locator = (By.XPATH,f'//div[@class="profile-picture"]/div/span[text()="{user_data["firstname"]} {user_data["lastname"]}"]')
        logged_in_user = self.WAIT.until(EC.visibility_of_element_located(logged_in_user_locator))
        assert logged_in_user.is_displayed() == True, "User is not logged in"
        with open(self.resource_path("tests/user_data.json"), mode="r") as data_file:
            data = json.load(data_file)
            data[user_data["username"]]["registered"] = True
        with open(self.resource_path("tests/user_data.json"), mode="w") as data_file:
            json.dump(data, data_file, indent=4)
