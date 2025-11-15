# base/base_driver.py
from appium import webdriver
from appium.options.common import AppiumOptions
from typing import Dict, Any

class BaseDriver:
    def __init__(self):
        self.driver = None

    def start_driver(self) -> None:
        caps: Dict[str, Any] = {
            "platformName": "Android",
            "appium:platformVersion": "16",
            "appium:udid": "emulator-5554",
            "appium:appPackage": "com.flipkart.android",
            "appium:appActivity": "com.flipkart.android.activity.HomeFragmentHolderActivity",
            "appium:automationName": "uiautomator2"
        }

        url = 'http://localhost:4723'
        self.driver = webdriver.Remote(url, options=AppiumOptions().load_capabilities(caps))
        self.driver.implicitly_wait(10)
        return self.driver

    def quit_driver(self) -> None:
        if self.driver:
            self.driver.quit()
