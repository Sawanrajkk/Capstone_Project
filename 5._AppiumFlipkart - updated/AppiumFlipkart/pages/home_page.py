# pages/home_page.py
import os
import time
import allure

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class HomePage:
    def __init__(self, driver, wait_seconds: int = 20):
        self.driver = driver
        self.wait = WebDriverWait(driver, wait_seconds)
        self.ss_dir = os.path.join("reports", "screenshots")
        os.makedirs(self.ss_dir, exist_ok=True)

    # -------------------- helpers --------------------

    def _attach_ss(self, filename: str, step_name: str):
        path = os.path.join(self.ss_dir, filename)
        try:
            self.driver.save_screenshot(path)
            allure.attach.file(path, name=step_name, attachment_type=allure.attachment_type.PNG)
        except Exception:
            pass

    def _click_first_that_exists(self, candidates, step_name="click"):
        """
        Try locators in order; return True on first success.
        candidates: list[(By, locator)]
        """
        for by, sel in candidates:
            try:
                el = self.wait.until(EC.element_to_be_clickable((by, sel)))
                el.click()
                time.sleep(0.25)
                return True
            except Exception:
                continue
        self._attach_ss(f"{step_name}_failed.png", f"{step_name} failed")
        return False

    # -------------------- onboarding / popups --------------------

    def allow_permissions(self):
        """
        Accept Android runtime permission dialog (location, etc).
        Safe to call; silently returns if nothing shows.
        """
        self.driver.implicitly_wait(0)
        try:
            # Newer Android permission controller
            for btn_id in [
                "com.android.permissioncontroller:id/permission_allow_foreground_only_button",  # While using the app
                "com.android.permissioncontroller:id/permission_allow_one_time_button",
                "com.android.permissioncontroller:id/permission_allow_button",
                "com.android.permissioncontroller:id/permission_allow_always_button",
            ]:
                try:
                    self.driver.find_element(AppiumBy.ID, btn_id).click()
                    break
                except NoSuchElementException:
                    pass

            # Legacy fallback
            for btn_id in [
                "com.android.packageinstaller:id/permission_allow_button",
                "com.android.packageinstaller:id/permission_allow_always_button",
                "com.android.packageinstaller:id/permission_allow_foreground_only_button",
            ]:
                try:
                    self.driver.find_element(AppiumBy.ID, btn_id).click()
                    break
                except NoSuchElementException:
                    pass

            # Text fallback
            for txt in ["While using the app", "Allow only while using the app", "Allow", "ALLOW"]:
                try:
                    self.driver.find_element(AppiumBy.XPATH, f"//android.widget.Button[@text='{txt}']").click()
                    break
                except NoSuchElementException:
                    pass
        finally:
            self.driver.implicitly_wait(10)
        time.sleep(0.4)

    def select_language_and_continue(self):
        """
        If a language selection sheet appears, pick English and continue.
        """
        self.driver.implicitly_wait(0)
        try:
            try:
                english = self.driver.find_element(By.XPATH, "//*[@text='English' or contains(@text,'English')]")
                english.click()
                for xp in [
                    "//*[@text='Continue']",
                    "//*[@text='CONTINUE']",
                    "//*[@text='Save']",
                    "//*[@text='SAVE']",
                    "//*[@text='Confirm']",
                    "//*[@text='CONFIRM']",
                    "//*[@resource-id='com.flipkart.android:id/btn_continue']",
                ]:
                    try:
                        self.driver.find_element(By.XPATH, xp).click()
                        break
                    except NoSuchElementException:
                        pass
            except NoSuchElementException:
                pass
        finally:
            self.driver.implicitly_wait(10)
        time.sleep(0.3)

    def skip_login(self):
        """
        Dismiss Flipkart login/upsell sheet if present (Skip / Maybe later / back icon).
        """
        self.driver.implicitly_wait(0)
        try:
            for xp in [
                "//*[@text='Skip' or @text='SKIP' or contains(@text,'Maybe later')]",
                "//android.widget.ImageButton[@content-desc='Close']",
                "//*[@resource-id='com.flipkart.android:id/custom_back_icon']",
                "//*[@resource-id='com.flipkart.android:id/btn_maybe_later']",
                "//*[@resource-id='com.flipkart.android:id/close_btn']",
            ]:
                try:
                    self.driver.find_element(By.XPATH, xp).click()
                    break
                except NoSuchElementException:
                    pass
        finally:
            self.driver.implicitly_wait(10)
        time.sleep(0.3)

    # -------------------- main actions --------------------

    def open_categories(self) -> bool:
        """
        Open the Categories page/card from the *home* screen.
        Prefer a11y id (stable in your XML): content-desc="Categories"
        """
        with allure.step("Open Categories"):
            ok = self._click_first_that_exists(
                [
                    (AppiumBy.ACCESSIBILITY_ID, "Categories"),
                    (By.XPATH, "//*[@content-desc='Categories']"),
                    (By.XPATH, "//android.widget.TextView[@text='Categories']/parent::*"),
                    # fallback example id (verify on your build with Inspector)
                    (By.ID, "com.flipkart.android:id/category_card"),
                ],
                step_name="open_categories"
            )
            if ok:
                print("✅ Categories opened successfully")
            else:
                print("⚠️ Failed to open categories")
            return ok

    def click_search_icon(self) -> bool:
        """
        Tap the search entry on *home* to open the dedicated search screen.
        Your XML shows the top search surface is a clickable ViewGroup, not EditText.
        We also avoid the 'Location not set' row.
        """
        with allure.step("Open search surface"):
            # Avoid the location row if possible
            try:
                loc_row = self.driver.find_elements(
                    By.XPATH, "//*[@content-desc and contains(@content-desc,'Select delivery location')]"
                )
                if loc_row:
                    # do nothing; we simply avoid tapping this area
                    pass
            except Exception:
                pass

            ok = self._click_first_that_exists(
                [
                    # Common ids when present
                    (By.ID, "com.flipkart.android:id/search_icon"),
                    (By.ID, "com.flipkart.android:id/search_widget_textbox"),
                    (AppiumBy.ACCESSIBILITY_ID, "Search"),

                    # From your XML: clickable top bar (bounds may vary across devices,
                    # but this works on your emulator dump)
                    (By.XPATH, "//android.widget.FrameLayout"
                               "/android.view.ViewGroup[@clickable='true' and @bounds='[385,148][696,263]']"),

                    # Generic fallback (second clickable viewgroup near top)
                    (By.XPATH, "(//android.view.ViewGroup[@clickable='true'])[2]"),

                    # As a last resort: any TextView that contains 'Search'
                    (By.XPATH, "//android.widget.TextView[contains(@text,'Search')]"),
                ],
                step_name="open_search"
            )

            if not ok:
                print("⚠️ Failed to click search icon")
                return False

            # Wait for the real EditText on the next screen so that caller can type
            try:
                self.wait.until(EC.any_of(
                    EC.presence_of_element_located((By.ID, "com.flipkart.android:id/search_autoCompleteTextView")),
                    EC.presence_of_element_located((By.ID, "com.flipkart.android:id/search_edit_text")),
                    EC.presence_of_element_located((By.CLASS_NAME, "android.widget.EditText")),
                    EC.presence_of_element_located((AppiumBy.XPATH, "//android.widget.EditText"))
                ))
            except TimeoutException:
                self._attach_ss("search_edittext_not_present.png", "search_edittext_wait")
                print("⚠️ Search screen did not present EditText in time")
                return False

            print("✅ Search icon clicked successfully")
            return True

    def search_product(self, product_name: str) -> bool:
        """
        Type a product into the search box and submit (press Enter).
        Assumes click_search_icon() has switched to the search screen.
        """
        with allure.step(f"Search for product: {product_name}"):
            try:
                candidates = [
                    (By.ID, "com.flipkart.android:id/search_autoCompleteTextView"),
                    (By.ID, "com.flipkart.android:id/search_edit_text"),
                    (AppiumBy.XPATH, "//android.widget.EditText[contains(@text,'Search')]"),
                    (By.CLASS_NAME, "android.widget.EditText"),
                ]
                el = None
                for by, sel in candidates:
                    try:
                        el = self.wait.until(EC.element_to_be_clickable((by, sel)))
                        break
                    except TimeoutException:
                        continue

                if not el:
                    self._attach_ss("search_product_no_box.png", "search_box_not_found")
                    print(f"⚠️ Search box not found for '{product_name}'")
                    return False

                try:
                    el.click()
                except Exception:
                    pass
                try:
                    el.clear()
                except Exception:
                    pass

                el.send_keys(product_name)
                # Press Enter to submit search
                self.driver.press_keycode(66)  # KEYCODE_ENTER
                time.sleep(1.0)
                print(f"✅ Searched for product: {product_name}")
                return True

            except Exception as e:
                print(f"⚠️ Failed to search for product '{product_name}': {e}")
                self._attach_ss("search_product_error.png", f"Search Product Error - {product_name}")
                return False
