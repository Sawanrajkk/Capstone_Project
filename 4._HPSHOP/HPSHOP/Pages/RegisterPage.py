from base.base_driver import BaseDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class RegisterPage(BaseDriver):
    def __init__(self,driver):
        super().__init__(driver)
        self.driver = driver

    def url(self):
       # wait = WebDriverWait(self.driver, 10)
       # wait.until(EC.url_contains("user_details"))
        self.wait_for_Url("user_details")
        current_url = self.driver.current_url
        assert "user_details" in current_url, f"❌ Expected 'user_details' in URL, but got {current_url}"
        print("✅ URL verified: 'user_details' is present in", current_url)
