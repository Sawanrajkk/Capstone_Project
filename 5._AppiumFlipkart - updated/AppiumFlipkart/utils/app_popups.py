# utils/app_popups.py
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def dismiss_flipkart_onboarding(driver, timeout=15):
    wait = WebDriverWait(driver, timeout)
    driver.implicitly_wait(0)
    try:
        # 1) Language selection (tap "English" then "Continue" / "Save" / "Confirm")
        try:
            english = wait.until(EC.presence_of_element_located((
                By.XPATH, "//*[@text='English' or contains(@text,'English')]"
            )))
            english.click()
            for xpath in [
                "//*[@text='Continue']",
                "//*[@text='CONTINUE']",
                "//*[@text='Save']",
                "//*[@text='SAVE']",
                "//*[@text='Confirm']",
                "//*[@text='CONFIRM']",
            ]:
                try:
                    btn = driver.find_element(By.XPATH, xpath)
                    btn.click()
                    break
                except NoSuchElementException:
                    pass
        except Exception:
            pass

        # 2) Login sheet – press Skip / Maybe later / X
        for xpath in [
            "//*[@text='Skip' or @text='SKIP' or contains(@text,'Maybe later')]",
            "//android.widget.ImageButton[@content-desc='Close']",
            "//*[@resource-id='com.flipkart.android:id/custom_back_icon']",
            "//*[@resource-id='com.flipkart.android:id/btn_maybe_later']",
        ]:
            try:
                el = driver.find_element(By.XPATH, xpath)
                el.click()
                break
            except NoSuchElementException:
                pass
    finally:
        driver.implicitly_wait(10)
