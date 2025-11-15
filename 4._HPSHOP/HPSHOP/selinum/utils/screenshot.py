import time
from pathlib import Path
import allure

BASE_DIR = Path(__file__).resolve().parents[2]
SCREENSHOT_ROOT = BASE_DIR / "screenshots"

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def get_timestamp():
    return time.strftime("%Y%m%d_%H%M%S")

def take_screenshot(driver, test_name: str, step: str, seq: int = None, attach_allure: bool = True) -> str:
    safe_test = test_name.replace("/", "_").replace("::", "_")
    folder = SCREENSHOT_ROOT / f"{safe_test}_{get_timestamp()}"
    ensure_dir(folder)
    seq_part = f"_{seq:02d}" if seq is not None else ""
    filename = f"{get_timestamp()}{seq_part}_{step}.png"
    filepath = folder / filename
    try:
        driver.save_screenshot(str(filepath))
    except Exception:
        try:
            png = driver.get_screenshot_as_png()
            with open(filepath, "wb") as f:
                f.write(png)
        except Exception:
            pass
    if attach_allure:
        try:
            with open(filepath, "rb") as f:
                allure.attach(f.read(), name=filename, attachment_type=allure.attachment_type.PNG)
        except Exception:
            pass
    return str(filepath)