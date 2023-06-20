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
from selenium.common.exceptions import TimeoutException,ElementNotInteractableException
import time
import names
import string
import random
import json
import os



class TestUser:
    # def __init__(self) -> None:
    service = Service()
    driver = webdriver.Chrome(service=service)
    WAIT = WebDriverWait(driver,6)
    tabs = {}

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

    def generate_user(self):
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


    def search_for_school(self):
        school_input_locator = (By.ID,'school-search')
        school_input = self.WAIT.until(EC.visibility_of_element_located(school_input_locator))
        try:
            school_input.send_keys("c")
        except ElementNotInteractableException:
            import pdb; pdb.set_trace()
        school_list_locator = (By.CSS_SELECTOR, 'ul[id^="ui-id"]')
        school_list = self.WAIT.until(EC.visibility_of_element_located(school_list_locator))
        school_item = school_list.find_element(By.XPATH,'//li[text()="Cranium Cafe - Test"]')
        # TODO assert the school is searchable using a variety of search terms
        school_item.click()


    def confirm_login_redirect(self):
        confirm_btn_locator = (By.ID,"integration-redirect-button")
        confirm_btn = self.WAIT.until(EC.element_to_be_clickable(confirm_btn_locator))
        confirm_btn.click()
        # close main tab
        self.driver.close()
        del self.tabs["conexed_main_tab"]


    def redirect_new_tab_handler(self):
        all_tabs = self.driver.window_handles
        for tab in all_tabs:
            if tab not in self.tabs.values():
                self.driver.switch_to.window(tab)
                self.tabs[self.driver.title] = tab
        return self.driver.title


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


    def switch_to_first_iframe(self):
        self.driver.switch_to.frame(0)


    def choose_guest_registration(self):
        login_method_btn = self.driver.find_element(By.CSS_SELECTOR,"button#craniumcafe-button")
        login_method_btn.click()
        # TODO assert modal loads
        register_toggle_button = self.driver.find_element(By.ID,"register-toggle-button")
        register_toggle_button.click()


    def fill_out_registration_form(self):
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
            import pdb; pdb.set_trace()
        create_password_entry = self.driver.find_element(By.ID,"create-password-text")
        create_password_entry.send_keys(password)
        confirm_password_entry = self.driver.find_element(By.ID,"confirm-password-text")
        confirm_password_entry.send_keys(password)
        # TODO assert form validations
        return email


    def submit_registration_form(self):
        register_btn = self.driver.find_element(By.ID,'register-button')
        register_btn.click()
        self.driver.close()
        del self.tabs["Login to ConexED"]


    def activate_temp_mailbox(self,user_data):
        email_parts = user_data["email"].split("@")
        username = email_parts[0]
        domain = email_parts[1]
        self.tab_switcher("tempmailbox_tab",f"https://www.fakemailgenerator.com/#/{domain}/{username}")


    def choose_guest_login(self):
        login_method_btn = self.driver.find_element(By.CSS_SELECTOR,"button#craniumcafe-button")
        login_method_btn.click()


    def enter_login_credentials(self):
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


    def submit_login(self):
        login_btn = self.driver.find_element(By.ID,"login-button")
        login_btn.click()


    def confirm_logged_in(self,user_data):
        # '//div[@class="profile-picture"]/div/span[text()="Jennifer Salak"]'
        logged_in_user_locator = (By.XPATH,f'//div[@class="profile-picture"]/div/span[text()="{user_data["firstname"]} {user_data["lastname"]}"]')
        logged_in_user = self.WAIT.until(EC.visibility_of_element_located(logged_in_user_locator))
        assert logged_in_user.is_displayed() == True, "User is not logged in"
        with open(self.resource_path("tests/user_data.json"), mode="r") as data_file:
            data = json.load(data_file)
            data[user_data["username"]]["registered"] = True
        with open(self.resource_path("tests/user_data.json"), mode="w") as data_file:
            json.dump(data, data_file, indent=4)

    def get_user_data(self):
        with open(self.resource_path("tests/user_data.json"), mode="r") as data_file:
            data = json.load(data_file)
        for user in data:
            if data[user]['registered'] == False:
                return data[user]
        return None

    def test_register(self):
        user_data = self.generate_user()
        self.activate_temp_mailbox(user_data)
        self.tab_switcher("conexed_main_tab","https://my.test.craniumcafe.com")
        self.search_for_school()
        self.confirm_login_redirect()
        self.redirect_new_tab_handler()
        self.switch_to_first_iframe()
        self.choose_guest_registration()
        self.fill_out_registration_form()
        self.submit_registration_form()
        return user_data

    def rgister_retry(self,user_data):
        try:
            if self.tabs["Login to ConexED"]:
                self.driver.switch_to.window(self.tabs["Login to ConexED"])
                del self.tabs["Login to ConexED"]
                self.driver.close()
        except KeyError:
            pass
        try:
            if self.tabs["conexed_main_tab"]:
                self.driver.switch_to.window(self.tabs["conexed_main_tab"])
                del self.tabs["conexed_main_tab"]
                self.driver.close()
        except KeyError:
            pass
        self.tab_switcher("conexed_main_tab","https://my.test.craniumcafe.com")
        self.search_for_school()
        self.confirm_login_redirect()
        self.redirect_new_tab_handler()
        self.switch_to_first_iframe()
        self.choose_guest_registration()
        self.fill_out_registration_form()
        self.submit_registration_form()
        self.test_confirm_registration(user_data)

    def test_confirm_registration(self):
        user_data = self.get_user_data()
        self.tab_switcher("tempmailbox_tab",f"https://www.fakemailgenerator.com/#/{user_data['domain']}/{user_data['username']}")
        email_frame_locator = (By.ID,"emailFrame")
        try:
            email_frame = WebDriverWait(self.driver,60).until(EC.visibility_of_element_located(email_frame_locator))
        except TimeoutException:
            print("Email not received")
            self.rgister_retry(user_data)
        else:
            self.driver.switch_to.frame(email_frame)
            register_link_locator = (By.XPATH,'//a[contains(text(),"https://cc.test.craniumcafe.com/register/")]')
            try:
                register_link = WebDriverWait(self.driver,15).until(EC.element_to_be_clickable(register_link_locator))
            except TimeoutException:
                print("Register link not found")
                import pdb; pdb.set_trace()
            else:
                register_link.click()
                self.redirect_new_tab_handler()
                # TODO assert "Thank you for registering!"
                self.tab_switcher("Login to ConexED","https://cc.test.craniumcafe.com/login")
                # Return to sign in
                try:
                    return_to_sign_in_btn = self.driver.find_element(By.LINK_TEXT,"Return to sign in")
                    return_to_sign_in_btn.click()
                except:
                    pass
        return user_data

    def test_login(self):
        user_data = self.get_user_data()
        self.tab_switcher("conexed_main_tab","https://my.test.craniumcafe.com")
        self.search_for_school()
        self.confirm_login_redirect()
        self.redirect_new_tab_handler()
        self.switch_to_first_iframe()
        self.choose_guest_login()
        self.enter_login_credentials()
        self.submit_login()
        self.confirm_logged_in(user_data)
        return user_data



# if __name__ == '__main__':
#     app = TestUser()
#     user_data = app.test_register()
#     # user_data = {
#     #     "firstname": "Rose",
#     #     "lastname": "Davis",
#     #     "username": "RoseDavis",
#     #     "domain": "dayrep.com",
#     #     "email": "RoseDavis@dayrep.com",
#     #     "password": "&7NYwAwwunNT9&",
#     #     "registered": False
#     # }
#     app.test_confirm_registration(user_data)
#     app.test_login(user_data)

#     # import pdb; pdb.set_trace()
#     time.sleep(3)
#     app.driver.quit()


