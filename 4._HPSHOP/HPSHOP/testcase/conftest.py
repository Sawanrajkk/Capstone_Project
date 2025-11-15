# testcase/conftest.py
# Robust conftest: make project root importable, prefer selinum.conftest fixtures,
# otherwise provide fallback driver and ss fixtures.

import os, sys

# ensure project root (one level up) is on sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Try to reuse fixtures from selinum.conftest if available
try:
    from selinum.conftest import driver, ss  # noqa: F401
    # If import succeeds, pytest will discover those fixtures from this module.
except Exception:
    # Fallback fixtures (webdriver-manager + simple screenshot helper)
    import pytest
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service as ChromeService
    try:
        from webdriver_manager.chrome import ChromeDriverManager
    except Exception:
        ChromeDriverManager = None

    @pytest.fixture(scope="function")
    def driver():
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        # options.add_argument("--headless=new")  # enable if desired
        if ChromeDriverManager is not None:
            service = ChromeService(ChromeDriverManager().install())
            drv = webdriver.Chrome(service=service, options=options)
        else:
            drv = webdriver.Chrome(options=options)  # requires chromedriver on PATH
        yield drv
        try:
            drv.quit()
        except Exception:
            pass

    @pytest.fixture(scope="function")
    def ss(request, driver):
        # simple screenshot helper that saves into ./screenshots/<testname>/
        import time
        from pathlib import Path
        import allure

        class SSHelper:
            def __init__(self):
                self.test_name = request.node.nodeid.replace("/", "_").replace("::", "_")
                self.seq = 0
                self.driver = driver
                self.root = Path(PROJECT_ROOT) / "screenshots"
            def _ensure(self):
                self.root.mkdir(parents=True, exist_ok=True)
            def take(self, step: str):
                self._ensure()
                self.seq += 1
                fname = f"{self.test_name}_{self.seq:02d}_{int(time.time())}_{step}.png"
                path = self.root / fname
                try:
                    driver.save_screenshot(str(path))
                except Exception:
                    try:
                        with open(path, "wb") as f:
                            f.write(driver.get_screenshot_as_png())
                    except Exception:
                        pass
                # try attach to allure if available
                try:
                    with open(path, "rb") as f:
                        allure.attach(f.read(), name=fname, attachment_type=allure.attachment_type.PNG)
                except Exception:
                    pass
                return str(path)
        return SSHelper()
