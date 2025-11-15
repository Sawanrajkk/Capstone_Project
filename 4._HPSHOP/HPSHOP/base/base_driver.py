from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class BaseDriver:
    def __init__(self,driver):
        self.driver = driver

    # function for waiting for the title of the page
    def wait_for_title(self,title):
        wait = WebDriverWait(self.driver, 20)
        wait.until(EC.title_is(title))

    #Function for waiting for visibility of element
    def wait_for_visibility_of_element_located(self,locator_type,locator):
        wait = WebDriverWait(self.driver, 20)
        wait.until(EC.visibility_of_element_located((locator_type,locator)))

    def wait_for_Url(self,url):
        wait = WebDriverWait(self.driver, 20)
        wait.until(EC.url_contains(url))

    def find_element(self,locator_type,locator):
        element = self.driver.find_element(locator_type,locator)
        return element