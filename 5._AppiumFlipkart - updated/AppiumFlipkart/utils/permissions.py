# utils/permissions.py
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

def allow_android_permissions(driver, timeout_secs=8):
    """
    Attempts to accept Android runtime permission dialogs.
    Supports both old (packageinstaller) and new (permissioncontroller) IDs,
    plus text-based fallbacks for different Android versions.
    Call this after app launch and before interacting with the app UI.
    """
    ids = [
        # Newer Android permission controller
        "com.android.permissioncontroller:id/permission_allow_foreground_only_button",
        "com.android.permissioncontroller:id/permission_allow_one_time_button",
        "com.android.permissioncontroller:id/permission_allow_button",
        "com.android.permissioncontroller:id/permission_allow_always_button",
        # Older package installer
        "com.android.packageinstaller:id/permission_allow_button",
        "com.android.packageinstaller:id/permission_allow_foreground_only_button",
        "com.android.packageinstaller:id/permission_allow_always_button",
    ]
    texts = [
        # Common button texts across versions/locales (add more if needed)
        "While using the app",
        "Only this time",
        "Allow",
        "ALLOW",
        "Allow only while using the app",
    ]

    driver.implicitly_wait(0)
    try:
        # Try id-based buttons first
        for _ in range(timeout_secs * 2):  # ~8s with 0.5s polls
            for btn_id in ids:
                try:
                    el = driver.find_element(By.ID, btn_id)
                    el.click()
                    driver.implicitly_wait(10)
                    return True
                except NoSuchElementException:
                    pass
            # Try text-based buttons
            for t in texts:
                xpath = f"//android.widget.Button[@text='{t}'] | //android.widget.Button[contains(@text,'{t}')]"
                try:
                    el = driver.find_element(By.XPATH, xpath)
                    el.click()
                    driver.implicitly_wait(10)
                    return True
                except NoSuchElementException:
                    pass
            # short sleep between polls
            driver.execute_script("mobile: sleep", {"duration": 500})
    finally:
        driver.implicitly_wait(10)
    return False
