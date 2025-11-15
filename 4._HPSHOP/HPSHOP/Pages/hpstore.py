"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import allure

class HPStorePage:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
        self.logs = []

    @allure.step("Opening HP Store website")
    def open_site(self):
        self.driver.get("https://store.hp.com/in-en/default/personal-laptops.html")
        self.logs.append("✅ Opened HP Store Website")

    def accept_cookies(self):
        try:
            accept_cookies = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Accept All Cookies')]"))
            )
            accept_cookies.click()
            self.logs.append("✅ Accepted cookies.")
        except:
            self.logs.append("ℹ️ Cookie popup not found or already handled.")

    def verify_title(self, expected_title):
        actual_title = self.driver.title
        self.logs.append(f"Actual title: {actual_title}")
        assert expected_title in actual_title, "❌ Title does not match!"
        self.logs.append("✅ Title verified!")

    def click_shop_now(self):
        time.sleep(2)
        try:
            shop_now = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[@class='c-button stack white-c']"))
            )
            shop_now.click()
            self.logs.append("✅ Clicked 'Shop Now'.")
        except:
            self.logs.append("ℹ️ 'Shop Now' button not found. Proceeding to search directly.")

    # 🆕 Search product method (locator updated)
    def search_product(self, product_name):
        try:
            # The HP store India search box has id='search'
            search_box = self.wait.until(EC.element_to_be_clickable((By.ID, "search")))
            search_box.clear()
            search_box.send_keys(product_name)
            search_box.submit()
            self.logs.append(f"🔍 Searched for product: {product_name}")
            time.sleep(3)  # Wait for search results to load
        except Exception as e:
            self.logs.append(f"❌ Unable to search for product. Error: {e}")

    def get_products(self):
        try:
            self.wait.until(
                lambda d: d.find_elements(By.XPATH, "//a[contains(@class,'product-item-link')]")
            )
            products = self.driver.find_elements(By.XPATH, "//a[contains(@class,'product-item-link')]")
            if not products:
                raise Exception("No products found on the page.")
            self.logs.append(f"✅ Number of products found: {len(products)}")
            return products
        except Exception as e:
            self.logs.append(f"❌ Could not load products. Error: {e}")
            self.driver.save_screenshot("error_products_not_found.png")
            raise

    def select_first_product(self, products):
        product_name = products[0].text
        self.logs.append(f"🛒 Selected Product Name (from listing): {product_name}")
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", products[0])
            time.sleep(1)
            products[0].click()
            self.logs.append("✅ Clicked on the first product.")
        except:
            self.driver.execute_script("arguments[0].click();", products[0])
            self.logs.append("⚡ Clicked first product using JS fallback.")
        return product_name

    def switch_to_product_window(self):
        windows = self.driver.window_handles
        self.driver.switch_to.window(windows[-1])

    def get_product_name_detail_page(self):
        product_detail_name = self.wait.until(
            EC.visibility_of_element_located((By.TAG_NAME, "h1"))
        )
        name_on_page = product_detail_name.text.strip()
        self.logs.append(f"🛒 Product Name on Product Page: {name_on_page}")
        return name_on_page

    def add_to_cart(self):
        add_to_cart_button = self.wait.until(EC.element_to_be_clickable((By.ID, "product-addtocart-button")))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_to_cart_button)
        time.sleep(3)
        add_to_cart_button.click()
        self.logs.append("✅ Clicked 'Add to cart' button.")
        self.logs.append("🎉 Item should now be in cart.")

    def open_cart(self):
        time.sleep(4)
        button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@class='action primary view-cart simple-popup-view-cart']")))
        button.click()
        self.logs.append("✅ Opened cart view.")

    def verify_cart_product(self, expected_name):
        cart_text = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[@class='stellar-title__small text-primary']")))
        self.logs.append(f"🛒 Product in cart: {cart_text[0].text}")
        assert cart_text[0].text.strip() == expected_name.strip(), \
            "❌ Product name in cart does not match the selected product."
        self.logs.append("✅ Product name in cart matches the selected product.")

    def inject_logs_and_screenshot(self):
        self.logs.append("👋 Bye!")
        self.driver.save_screenshot("final_page.png")
        js_code = f'''
        var logDiv = document.createElement('pre');
        logDiv.style.fontSize = '16px';
        logDiv.style.color = 'black';
        logDiv.style.background = 'white';
        logDiv.style.position = 'absolute';
        logDiv.style.top = '0';
        logDiv.style.left = '0';
        logDiv.style.zIndex = '999999';
        logDiv.style.padding = '20px';
        logDiv.style.width = '100%';
        logDiv.style.height = '100%';
        logDiv.style.overflow = 'auto';
        logDiv.innerText = `{chr(10).join(self.logs)}`;
        document.body.innerHTML = '';
        document.body.appendChild(logDiv);
        '''
        self.driver.execute_script(js_code)
        self.driver.save_screenshot("console_output.png")
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import allure

class HPStorePage:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
        self.logs = []

    @allure.step("Opening HP Store website")
    def open_site(self):
        self.driver.get("https://store.hp.com/in-en/default/personal-laptops.html")
        self.logs.append("Opened HP Store Website")

    def accept_cookies(self):
        try:
            accept_cookies = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Accept All Cookies')]"))
            )
            accept_cookies.click()
            self.logs.append("Accepted cookies.")
        except:
            self.logs.append("Cookie popup not found or already handled.")

    def verify_title(self, expected_title):
        actual_title = self.driver.title
        self.logs.append(f"Actual title: {actual_title}")
        assert expected_title in actual_title, "Title does not match!"
        self.logs.append("Title verified!")

    def click_shop_now(self):
        time.sleep(2)
        try:
            shop_now = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[@class='c-button stack white-c']"))
            )
            shop_now.click()
            self.logs.append("Clicked 'Shop Now'.")
        except:
            self.logs.append("'Shop Now' button not found. Proceeding to search directly.")

    def search_product(self, product_name):
        try:
            search_box = self.wait.until(EC.element_to_be_clickable((By.ID, "search")))
            search_box.clear()
            search_box.send_keys(product_name)
            search_box.submit()
            self.logs.append(f"Searched for product: {product_name}")
            time.sleep(3)  # Wait for search results to load
        except Exception as e:
            self.logs.append(f"Unable to search for product. Error: {e}")

    def get_products(self):
        try:
            self.wait.until(
                lambda d: d.find_elements(By.XPATH, "//a[contains(@class,'product-item-link')]")
            )
            products = self.driver.find_elements(By.XPATH, "//a[contains(@class,'product-item-link')]")
            if not products:
                raise Exception("No products found on the page.")
            self.logs.append(f"Number of products found: {len(products)}")
            return products
        except Exception as e:
            self.logs.append(f"Could not load products. Error: {e}")
            self.driver.save_screenshot("error_products_not_found.png")
            raise

    def select_first_product(self, products):
        product_name = products[0].text
        self.logs.append(f"Selected Product Name (from listing): {product_name}")
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", products[0])
            time.sleep(1)
            products[0].click()
            self.logs.append("Clicked on the first product.")
        except:
            self.driver.execute_script("arguments[0].click();", products[0])
            self.logs.append("Clicked first product using JS fallback.")
        return product_name

    def switch_to_product_window(self):
        windows = self.driver.window_handles
        self.driver.switch_to.window(windows[-1])

    def get_product_name_detail_page(self):
        product_detail_name = self.wait.until(
            EC.visibility_of_element_located((By.TAG_NAME, "h1"))
        )
        name_on_page = product_detail_name.text.strip()
        self.logs.append(f"Product Name on Product Page: {name_on_page}")
        return name_on_page

    def add_to_cart(self):
        add_to_cart_button = self.wait.until(EC.element_to_be_clickable((By.ID, "product-addtocart-button")))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_to_cart_button)
        time.sleep(3)
        add_to_cart_button.click()
        self.logs.append("Clicked 'Add to cart' button.")
        self.logs.append("Item should now be in cart.")

    def open_cart(self):
        time.sleep(4)
        button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@class='action primary view-cart simple-popup-view-cart']")))
        button.click()
        self.logs.append("Opened cart view.")

    def verify_cart_product(self, expected_name):
        cart_text = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[@class='stellar-title__small text-primary']")))
        self.logs.append(f"Product in cart: {cart_text[0].text}")
        assert cart_text[0].text.strip() == expected_name.strip(), \
            " Product name in cart does not match the selected product."
        self.logs.append("Product name in cart matches the selected product.")

    def inject_logs_and_screenshot(self):
        self.logs.append("Bye!")
        self.driver.save_screenshot("final_page.png")
        js_code = f'''
        var logDiv = document.createElement('pre');
        logDiv.style.fontSize = '16px';
        logDiv.style.color = 'black';
        logDiv.style.background = 'white';
        logDiv.style.position = 'absolute';
        logDiv.style.top = '0';
        logDiv.style.left = '0';
        logDiv.style.zIndex = '999999';
        logDiv.style.padding = '20px';
        logDiv.style.width = '100%';
        logDiv.style.height = '100%';
        logDiv.style.overflow = 'auto';
        logDiv.innerText = `{chr(10).join(self.logs)}`;
        document.body.innerHTML = '';
        document.body.appendChild(logDiv);
        '''
        self.driver.execute_script(js_code)
        self.driver.save_screenshot("console_output.png")
