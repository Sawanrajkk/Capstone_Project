from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def try_accept_alert(driver, timeout=1):
    try:
        alert = driver.switch_to.alert
        alert.accept()
        return True
    except NoAlertPresentException:
        return False

def close_modal_by_close_button(driver, selectors):
    for by, sel in selectors:
        try:
            btn = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((by, sel)))
            btn.click()
            return True
        except Exception:
            continue
    return False

def press_escape(driver):
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.ESCAPE)
        return True
    except Exception:
        return False

def remove_element_by_js(driver, css_selector):
    try:
        return driver.execute_script("""var el = document.querySelector(arguments[0]); if (el) { el.parentNode.removeChild(el); return true; } return false;""", css_selector)
    except Exception:
        return False

def dismiss_known_popups(driver):
    if try_accept_alert(driver):
        return "alert_accepted"
    close_selectors = [
        (By.CSS_SELECTOR, ".modal-close"),
        (By.CSS_SELECTOR, ".close-btn"),
        (By.CSS_SELECTOR, ".cookie-consent__close"),
        (By.CSS_SELECTOR, ".popup-close"),
        (By.XPATH, "//button[contains(text(),'No thanks')]"),
        (By.XPATH, "//button[contains(@aria-label,'close')]"),
    ]
    if close_modal_by_close_button(driver, close_selectors):
        return "button_closed"
    try:
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for idx, fr in enumerate(iframes[:5]):
            try:
                driver.switch_to.frame(fr)
                if close_modal_by_close_button(driver, close_selectors):
                    driver.switch_to.default_content()
                    return f"iframe_closed_idx_{idx}"
            except Exception:
                pass
            finally:
                try:
                    driver.switch_to.default_content()
                except Exception:
                    pass
    except Exception:
        pass
    try:
        press_escape(driver)
    except Exception:
        pass
    try:
        remove_element_by_js(driver, ".popup, .modal, .overlay")
        return "js_removed"
    except Exception:
        return "not_handled"