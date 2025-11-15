# testcase/test_hpstore.py
import os
import inspect
import pytest
from selenium.webdriver.support.ui import WebDriverWait

# Try multiple import paths for HPStorePage (project variations)
HPStorePage = None
_import_errors = []
for mod_path in ("Pages.hpstore", "pages.hpstore", "selinum.pages.hpstore", "selinum.Pages.hpstore"):
    try:
        module = __import__(mod_path, fromlist=["HPStorePage"])
        HPStorePage = getattr(module, "HPStorePage", None)
        if HPStorePage is None:
            raise ImportError(f"module '{mod_path}' imported but HPStorePage not found")
        break
    except Exception as e:
        _import_errors.append((mod_path, repr(e)))

if HPStorePage is None:
    msgs = "\n".join([f"{m}: {err}" for m, err in _import_errors])
    raise ImportError(
        "Could not import HPStorePage. Tried:\n" f"{msgs}\n\nEnsure hpstore.py defines `HPStorePage`."
    )

# Import excel reader
try:
    from selinum.utils.excel_reader import read_column
except Exception:
    # fallback minimal excel reader if needed (requires openpyxl)
    try:
        import openpyxl

        def read_column(file_path, sheet_name="Sheet1", col=1, header=False):
            wb = openpyxl.load_workbook(file_path, data_only=True)
            sheet = wb[sheet_name]
            start = 2 if header else 1
            vals = []
            for row in sheet.iter_rows(min_row=start, values_only=True):
                v = row[col - 1]
                if v is None:
                    continue
                vals.append(str(v).strip())
            return vals

    except Exception as e:
        raise ImportError("Couldn't import selinum.utils.excel_reader and openpyxl fallback failed.") from e

# Find products.xlsx
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
candidates = [
    os.path.join(BASE_DIR, "selinum", "resources", "products.xlsx"),
    os.path.join(BASE_DIR, "resources", "products.xlsx"),
    os.path.join(BASE_DIR, "products.xlsx"),
]
PRODUCTS_FILE = next((p for p in candidates if os.path.exists(p)), None)
if PRODUCTS_FILE is None:
    raise FileNotFoundError("products.xlsx not found. Checked:\n" + "\n".join(candidates))

products = read_column(PRODUCTS_FILE, sheet_name="Sheet1", col=1, header=True)
if not products:
    raise ValueError("No products read from Excel.")

# helper
def call_method(obj, name, *args, **kwargs):
    if not hasattr(obj, name):
        available = ", ".join([n for n in dir(obj) if not n.startswith("_")][:200])
        raise AttributeError(f"Required method '{name}' not found on {obj.__class__.__name__}. Available: {available}")
    return getattr(obj, name)(*args, **kwargs)


@pytest.mark.parametrize("product_name", products)
def test_hp_store_cart_excel(driver, ss, product_name):
    # instantiate HPStorePage; pass WebDriverWait if constructor requires it
    try:
        sig = inspect.signature(HPStorePage.__init__)
        params = list(sig.parameters.keys())
        if "wait" in params or "timeout" in params:
            hp = HPStorePage(driver, WebDriverWait(driver, 10))
        else:
            hp = HPStorePage(driver)
    except Exception:
        # fallback tries both forms
        try:
            hp = HPStorePage(driver)
        except TypeError:
            hp = HPStorePage(driver, WebDriverWait(driver, 10))

    # start: open home -> try open_homepage else open_site
    if hasattr(hp, "open_homepage"):
        call_method(hp, "open_homepage")
    elif hasattr(hp, "open_site"):
        call_method(hp, "open_site")
    else:
        # no site opener present — give informative error listing available methods
        available = ", ".join([n for n in dir(hp) if not n.startswith("_")][:200])
        raise AttributeError(f"No homepage opener found on HPStorePage. Expected 'open_homepage' or 'open_site'. Available: {available}")

    ss.take(f"home_loaded_{product_name}")

    # accept cookies if available
    if hasattr(hp, "accept_cookies"):
        call_method(hp, "accept_cookies")

    # navigate to shop (optional)
    if hasattr(hp, "click_shop_now"):
        call_method(hp, "click_shop_now")
        ss.take(f"after_click_shop_{product_name}")

    # search product
    call_method(hp, "search_product", product_name)
    ss.take(f"after_search_{product_name}")

    # get products and assert
    products_list = call_method(hp, "get_products")
    assert products_list, "No products returned from search"

    # select product
    if hasattr(hp, "select_first_product"):
        selected_product = call_method(hp, "select_first_product", products_list)
    elif hasattr(hp, "select_product"):
        selected_product = call_method(hp, "select_product", products_list[0])
    else:
        raise AttributeError("No selection method found (select_first_product/select_product).")

    # product detail
    if hasattr(hp, "switch_to_product_window"):
        call_method(hp, "switch_to_product_window")

    if hasattr(hp, "get_product_name_detail_page"):
        call_method(hp, "get_product_name_detail_page")

    ss.take(f"product_page_{product_name}")

    # add to cart
    call_method(hp, "add_to_cart")
    ss.take(f"after_add_to_cart_{product_name}")

    # open cart
    if hasattr(hp, "open_cart"):
        call_method(hp, "open_cart")
    elif hasattr(hp, "go_to_cart"):
        call_method(hp, "go_to_cart")
    else:
        raise AttributeError("No method found to open cart (open_cart/go_to_cart).")

    ss.take(f"cart_opened_{product_name}")

    # verify product present
    if hasattr(hp, "verify_cart_product"):
        call_method(hp, "verify_cart_product", selected_product)
    elif hasattr(hp, "is_product_in_cart"):
        assert call_method(hp, "is_product_in_cart", selected_product)
    else:
        raise AttributeError("No cart verification method found (verify_cart_product/is_product_in_cart).")

    ss.take(f"end_test_{product_name}")
