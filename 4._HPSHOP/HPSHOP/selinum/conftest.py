import pytest
from selenium import webdriver
from selinum.utils.screenshot import take_screenshot
import os, sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


@pytest.fixture(scope="function")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # options.add_argument("--headless=new")  # enable for CI
    drv = webdriver.Chrome(options=options)
    yield drv
    try:
        drv.quit()
    except Exception:
        pass

@pytest.fixture(scope="function")
def ss(request, driver):
    class SSHelper:
        def __init__(self):
            self.test_name = request.node.nodeid
            self.seq = 0
            self.driver = driver
        def take(self, step: str):
            self.seq += 1
            return take_screenshot(self.driver, self.test_name, step, self.seq)
    helper = SSHelper()
    yield helper

def pytest_runtest_makereport(item, call):
    if call.when == "call":
        driver_fixture = item.funcargs.get("driver") if "driver" in item.funcargs else None
        if driver_fixture:
            try:
                take_screenshot(driver_fixture, item.nodeid, "final_state", seq=999)
            except Exception:
                pass