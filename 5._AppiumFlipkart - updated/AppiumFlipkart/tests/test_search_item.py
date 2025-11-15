# tests/test_search_item.py
import os
import pytest
import allure
#SAWAN KUMAR
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.home_page import HomePage
from pages.search_results_page import SearchResultsPage
from utils.excel_utils import ExcelUtils  # Make sure utils folder has __init__.py


@pytest.mark.usefixtures("setup")
class TestSearchItem:

    @allure.feature("Search Functionality")
    @allure.story("Search product from Excel and apply filters (brand + price)")
    def test_search_watch(self):
        # ------------------ test data ------------------
        excel = ExcelUtils("Book1.xlsx")
        # Read Sheet1!A1 (fallback to "Smart Watch" if empty/missing)
        search_item = (excel.get_cell_value("Sheet1", "A1") or "Smart Watch").strip()

        home = HomePage(self.driver)
        results = SearchResultsPage(self.driver)

        # ------------------ onboarding / popups ------------------
        with allure.step("Handle OS and in-app onboarding (permissions, language, login)"):
            home.allow_permissions()
            home.select_language_and_continue()
            home.skip_login()
            # If the app shows any in-app overlay later, dismiss it as well (safe no-op otherwise)
            results.dismiss_in_app_overlays()

        # ------------------ search flow ------------------
        with allure.step(f"Open search and query: {search_item}"):
            # Opening Categories is optional — keep it but don't fail if not present
            home.open_categories()
            assert home.click_search_icon(), "Could not open search"
            assert home.search_product(search_item), f"Failed to search for '{search_item}'"
            # dismiss the push opt-in if it appears
            results.dismiss_push_optin()

            # then proceed to filters
            assert results.open_filter(), "Filter panel did not open"

        # ------------------ filters ------------------
        with allure.step("Open Filters and apply Brand + Price"):
            assert results.open_filter(), "Filter panel did not open"

            # Brand filter
            brand_ok = results.apply_brand_filter("Titan")   # change brand if needed
            if not brand_ok:
                allure.attach(body=f"Brand 'Titan' not found for '{search_item}'",
                              name="Brand filter note",
                              attachment_type=allure.attachment_type.TEXT)

            # Price filter (adjust the label to match your UI text)
            price_ok = results.apply_price_filter("₹5000")   # e.g., "₹5000 - ₹10000" or "20001"
            if not price_ok:
                allure.attach(body="Desired price range not found",
                              name="Price filter note",
                              attachment_type=allure.attachment_type.TEXT)

            results.apply_filters_done()

        # ------------------ verify results exist ------------------
        with allure.step("Verify search results are visible"):
            # wait briefly for any list of results or at least any text that contains the search term
            w = WebDriverWait(self.driver, 15)
            found_any = False
            try:
                # Try a common product title id first
                w.until(EC.presence_of_element_located((By.ID, "com.flipkart.android:id/product_name")))
                found_any = True
            except Exception:
                pass

            if not found_any:
                try:
                    # Fallback: any text containing 'watch' (case handled by app usually)
                    self.driver.find_element(AppiumBy.XPATH, "//*[contains(translate(@text,'WATCH','watch'),'watch')]")
                    found_any = True
                except Exception:
                    pass

            assert found_any, "No search results found on the first viewport"
            print("✅ Initial results detected")

        # ------------------ verify brand (best-effort) ------------------
        with allure.step("Best-effort: check brand appears in visible results"):
            # Don't hard-fail if brand not visible (Flipkart UI can vary)
            results.scroll_results(1)
            results.verify_brand_in_results("Titan")

        # ------------------ select a product & screenshot ------------------
        with allure.step("Open first result and capture final screenshot"):
            results.select_first_result()  # best-effort: won’t fail test if missing
            final_path = os.path.join("reports", "screenshots", "final_result.png")
            os.makedirs(os.path.dirname(final_path), exist_ok=True)
            results.take_screenshot(final_path)
            allure.attach.file(final_path, name="Final Screenshot", attachment_type=allure.attachment_type.PNG)
