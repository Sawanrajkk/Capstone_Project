# pages/search_results_page.py
import os
import time
import allure
import logging

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

log = logging.getLogger(__name__)


class SearchResultsPage:
    """
    Interacts with Search results + Filters.

    Guidelines:
    - Prefer resource-id, then accessibility id, then text/xpath.
    - Methods return True/False for tests to assert.
    - Minimize sleeps; prefer explicit waits.
    - Screenshots stored in reports/screenshots and attached to Allure.
    """

    def __init__(self, driver, wait_seconds: int = 12):
        self.driver = driver
        # Default explicit wait; keep moderate so tests don't hang too long.
        self.wait_seconds = wait_seconds
        self.wait = WebDriverWait(driver, wait_seconds)
        self.ss_dir = os.path.join("reports", "screenshots")
        os.makedirs(self.ss_dir, exist_ok=True)

    # ------------------------ helpers ------------------------

    def _attach_ss(self, fname: str, step_name: str) -> str:
        path = os.path.join(self.ss_dir, fname)
        try:
            self.driver.save_screenshot(path)
            allure.attach.file(path, name=step_name, attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            log.debug("screenshot attach failed: %s", e)
        return path

    def _click_first_that_exists(self, candidates, step_name="click", timeout=None) -> bool:
        """
        Try each (By, locator) until one is clickable and clicked.
        Returns True on first success, False otherwise.
        """
        timeout = timeout or self.wait_seconds
        w = WebDriverWait(self.driver, timeout)
        for by, sel in candidates:
            try:
                el = w.until(EC.element_to_be_clickable((by, sel)))
                el.click()
                # tiny pause to let UI update
                time.sleep(0.25)
                return True
            except Exception:
                continue

        self._attach_ss(f"{step_name}_failed.png", f"{step_name} failed")
        return False

    def _scroll_to_text_contains(self, text: str, scrollable=True) -> bool:
        """
        Use UiScrollable to bring 'text' into view. Returns True if element is located (no click).
        """
        try:
            self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiScrollable(new UiSelector().scrollable(%s)).scrollIntoView('
                'new UiSelector().textContains("%s"))' % (str(scrollable).lower(), text)
            )
            return True
        except Exception:
            return False

    def _wait_results_any(self, timeout: int = 10) -> bool:
        """
        Wait for any sign of results (to ensure toolbar stable).
        """
        probes = [
            (By.ID, "com.flipkart.android:id/product_name"),
            (By.ID, "com.flipkart.android:id/title"),
            (AppiumBy.XPATH, "//*[contains(translate(@text,'WATCH','watch'),'watch')]"),
        ]
        w = WebDriverWait(self.driver, timeout)
        for by, sel in probes:
            try:
                w.until(EC.presence_of_element_located((by, sel)))
                return True
            except TimeoutException:
                continue
        return False

    # ------------------------ overlays & popups ------------------------

    def dismiss_in_app_overlays(self):
        """
        Dismiss language + login overlays if present.
        Safe to call anytime (no-op if not present).
        """
        # temporarily reduce implicit wait to speed element lookups for these quick checks
        self.driver.implicitly_wait(0)
        try:
            # language selection -> pick 'English' if visible, then Continue/Save/Confirm
            try:
                english = self.driver.find_element(By.XPATH, "//*[@text='English' or contains(@text,'English')]")
                if english:
                    english.click()
                    for x in (
                        "//*[@text='Continue']",
                        "//*[@text='CONTINUE']",
                        "//*[@text='Save']",
                        "//*[@text='SAVE']",
                        "//*[@text='Confirm']",
                        "//*[@text='CONFIRM']",
                    ):
                        try:
                            self.driver.find_element(By.XPATH, x).click()
                            break
                        except NoSuchElementException:
                            pass
            except NoSuchElementException:
                pass

            # login sheet: Skip / Maybe later / Close
            for x in (
                "//*[@text='Skip' or @text='SKIP' or contains(@text,'Maybe later')]",
                "//android.widget.ImageButton[@content-desc='Close']",
                "//*[@resource-id='com.flipkart.android:id/custom_back_icon']",
                "//*[@resource-id='com.flipkart.android:id/btn_maybe_later']",
            ):
                try:
                    el = self.driver.find_element(By.XPATH, x)
                    if el:
                        el.click()
                        break
                except NoSuchElementException:
                    pass

        finally:
            self.driver.implicitly_wait(10)

    def dismiss_push_optin(self, timeout: int = 2) -> bool:
        """
        Dismiss the 'Allow Flipkart App to send notifications' dialog by clicking 'NOT NOW' (or fallback).
        Returns True if dismissed.
        """
        self.driver.implicitly_wait(0)
        try:
            # quick presence check for dialog text (optional)
            try:
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(@text,'notifications') or contains(@text,'Allow Flipkart App')]"))
                )
            except Exception:
                # if the dialog text didn't appear quickly, still try candidate buttons
                pass

            candidates = [
                (By.XPATH, "//*[@text='NOT NOW']"),
                (By.XPATH, "//*[@text='Not now']"),
                (By.XPATH, "//*[@text='Not Now']"),
                (By.ID, "com.flipkart.android:id/not_now"),  # guessed id (keep but optional)
                (By.XPATH, "//android.widget.Button[contains(@text,'NOT NOW') or contains(@text,'Not now')]"),
            ]

            for by, sel in candidates:
                els = self.driver.find_elements(by, sel)
                if els:
                    try:
                        els[0].click()
                        time.sleep(0.2)
                        print("✅ Dismissed push opt-in (NOT NOW)")
                        return True
                    except Exception:
                        continue

            # fallback: click first visible button in the dialog (left button usually)
            try:
                buttons = self.driver.find_elements(By.CLASS_NAME, "android.widget.Button")
                if buttons:
                    buttons[0].click()
                    time.sleep(0.2)
                    print("✅ Dismissed push opt-in via fallback button click")
                    return True
            except Exception:
                pass

            return False
        finally:
            self.driver.implicitly_wait(10)

    # ------------------------ filters flow ------------------------

    def open_filter(self, timeout: int = 12) -> bool:
        """
        Open the Filter panel. Returns True if panel opened / detected.
        """
        with allure.step("Open Filters"):
            # make sure results are present (sometimes toolbar only stabilizes after results)
            self._wait_results_any(timeout=8)

            candidates = [
                (By.ID, "com.flipkart.android:id/filter_button"),
                (By.ID, "com.flipkart.android:id/menu_filter"),
                (By.ID, "com.flipkart.android:id/sort_filter_view"),
                (AppiumBy.ACCESSIBILITY_ID, "Filters"),
                (AppiumBy.ACCESSIBILITY_ID, "Filter"),
                (AppiumBy.XPATH, "//*[@text='Filters' or @text='Filter']"),
            ]

            # Try clicking; if toolbar hidden, swipe a bit and retry once
            for attempt in range(2):
                if self._click_first_that_exists(candidates, step_name="open_filter", timeout=timeout):
                    # wait for any filter panel indicator
                    try:
                        WebDriverWait(self.driver, 4).until(
                            EC.presence_of_element_located((By.ID, "com.flipkart.android:id/filter_container"))
                        )
                    except Exception:
                        # fallback: brand/price text presence
                        try:
                            WebDriverWait(self.driver, 4).until(
                                EC.presence_of_element_located((AppiumBy.XPATH, "//*[contains(@text,'Brand') or contains(@text,'Price')]"))
                            )
                        except Exception:
                            pass
                    print("✅ Filter button clicked successfully")
                    return True

                # small swipe up to reveal toolbar
                try:
                    self.driver.swipe(start_x=500, start_y=1000, end_x=500, end_y=350, duration=500)
                except Exception:
                    pass

            # overflow menu fallback
            try:
                more = self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, "More options")
                if more:
                    more.click()
                    elm = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((AppiumBy.XPATH, "//*[@text='Filters' or @text='Filter']"))
                    )
                    elm.click()
                    print("✅ Filter opened via overflow menu")
                    return True
            except Exception:
                pass

            print("⚠️ Failed to click Filter button")
            self._attach_ss("open_filter_failed.png", "Filter Button Error")
            return False

    def apply_brand_filter(self, brand_name: str = "Titan") -> bool:
        """
        Open 'Brand' section and select brand_name. Returns True if brand clicked.
        """
        with allure.step(f"Apply brand filter: {brand_name}"):
            # open Brand section
            if not self._scroll_to_text_contains("Brand"):
                log.debug("Brand not immediately visible; attempting to open by xpath/id")
            opened = self._click_first_that_exists(
                [
                    (By.XPATH, "//*[contains(@text,'Brand')]"),
                    (By.ID, "com.flipkart.android:id/brand_title"),
                ],
                step_name="open_brand_section",
                timeout=8
            )
            if not opened:
                print("⚠️ Brand section not found")
                return False

            # try to scroll to brand; if not visible try filter's search
            if not self._scroll_to_text_contains(brand_name):
                print(f"⚠️ Could not scroll to brand '{brand_name}', trying brand-search input")
                try:
                    search_in_filter = self.driver.find_element(By.ID, "com.flipkart.android:id/search_text")
                    if search_in_filter:
                        search_in_filter.clear()
                        search_in_filter.send_keys(brand_name)
                        time.sleep(0.4)
                except Exception:
                    pass

            selected = self._click_first_that_exists(
                [
                    (By.XPATH, f"//*[contains(@text,'{brand_name}')]"),
                ],
                step_name="select_brand",
                timeout=6
            )
            if not selected:
                print(f"⚠️ Brand '{brand_name}' not found")
                try:
                    self.driver.back()
                except Exception:
                    pass
                return False

            print(f"✅ Selected brand: {brand_name}")
            return True

    def apply_price_filter(self, label_contains: str = "₹5000") -> bool:
        """
        Open 'Price' and select an option containing label_contains. Returns True on success.
        """
        with allure.step(f"Apply price filter: contains '{label_contains}'"):
            if not self._scroll_to_text_contains("Price"):
                print("⚠️ Price section not in view; trying alternate locators")
            opened = self._click_first_that_exists(
                [
                    (By.XPATH, "//*[contains(@text,'Price')]"),
                    (By.ID, "com.flipkart.android:id/price_title"),
                ],
                step_name="open_price_section",
                timeout=8
            )
            if not opened:
                print("⚠️ Price section not found")
                return False

            if not self._scroll_to_text_contains(label_contains):
                print(f"⚠️ Price option '{label_contains}' not visible after scroll")

            picked = self._click_first_that_exists(
                [
                    (By.XPATH, f"//*[contains(@text,'{label_contains}')]"),
                ],
                step_name="pick_price_option",
                timeout=6
            )
            if not picked:
                print(f"⚠️ Price range '{label_contains}' not found")
                try:
                    self.driver.back()
                except Exception:
                    pass
                return False

            print(f"✅ Selected price containing {label_contains}")
            return True

    def apply_filters_done(self) -> bool:
        """
        Confirm filters: click Apply/Show results or fallback to back (auto-apply).
        Returns True if explicit Apply clicked; False if fallback/back used.
        """
        with allure.step("Confirm filters (Apply/Show results)"):
            clicked = self._click_first_that_exists(
                [
                    (By.ID, "com.flipkart.android:id/apply_btn"),
                    (By.XPATH, "//*[contains(@text,'Apply') or contains(@text,'SHOW RESULTS') or contains(@text,'Show results')]"),
                ],
                step_name="confirm_filters",
                timeout=8
            )
            if clicked:
                print("✅ Applied filter successfully")
                self._wait_results_any(timeout=10)
                return True

            # fallback: back to results (some builds auto apply)
            try:
                self.driver.back()
                print("⚠️ Apply button not found; navigated back to results (auto-apply likely)")
            except Exception:
                pass
            self._wait_results_any(timeout=8)
            return False

    # ------------------------ verification & navigation ------------------------

    def verify_brand_in_results(self, brand_name: str = "Titan") -> bool:
        """
        Check first viewport product titles/subtitles for brand_name.
        """
        with allure.step(f"Verify brand in results: {brand_name}"):
            try:
                probes = [
                    (By.ID, "com.flipkart.android:id/product_name"),
                    (By.ID, "com.flipkart.android:id/title"),
                    (By.XPATH, f"//*[contains(@text,'{brand_name}')]"),
                ]
                for by, sel in probes:
                    elements = self.driver.find_elements(by, sel)
                    for el in elements:
                        if brand_name.lower() in (el.text or "").lower():
                            print(f"✅ Brand '{brand_name}' found in results")
                            return True

                self._attach_ss("verify_brand_failed.png", "brand_verify_failed")
                print(f"⚠️ Brand '{brand_name}' not visible in first viewport")
                return False
            except Exception as e:
                print(f"⚠️ Unexpected error verifying brand '{brand_name}': {e}")
                self._attach_ss("verify_brand_error.png", "brand_verify_error")
                return False

    def scroll_results(self, scroll_count: int = 1):
        """
        Perform vertical swipes in results list. Adjust coords for your emulator/device if needed.
        """
        with allure.step(f"Scroll results {scroll_count} time(s)"):
            for i in range(scroll_count):
                try:
                    self.driver.swipe(start_x=500, start_y=1200, end_x=500, end_y=400, duration=600)
                    print(f"✅ Scrolled {i + 1} time(s)")
                    time.sleep(0.3)
                except Exception as e:
                    print(f"⚠️ Unexpected error while scrolling: {e}")
                    self._attach_ss("scroll_results_unexpected_error.png", "scroll_error")
                    break

    def select_first_result(self) -> bool:
        """
        Click first visible product. Returns True on click.
        """
        with allure.step("Select first product"):
            for by, sel in (
                (By.ID, "com.flipkart.android:id/product_name"),
                (By.ID, "com.flipkart.android:id/title"),
                (By.XPATH, "(//android.widget.TextView)[1]"),
            ):
                try:
                    el = WebDriverWait(self.driver, 8).until(EC.presence_of_element_located((by, sel)))
                    el.click()
                    print("✅ First product selected")
                    return True
                except Exception:
                    continue
            self._attach_ss("select_first_result_failed.png", "select_result_failed")
            print("⚠️ Product name element not found. Maybe page took longer to load.")
            return False

    def take_screenshot(self, filename: str):
        """
        Save a full-screen screenshot to the given path and attach to Allure.
        """
        time.sleep(0.5)
        try:
            self.driver.get_screenshot_as_file(filename)
            allure.attach.file(filename, name="final_screenshot", attachment_type=allure.attachment_type.PNG)
            print(f"✅ Screenshot saved: {filename}")
        except Exception as e:
            print(f"⚠️ Failed to save screenshot {filename}: {e}")
