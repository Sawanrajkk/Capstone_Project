# TODO: Fix File Duplication and Improve Automation Script

## 1. Fix File Duplication Issues
- [x] Create `pytest.ini` to configure Allure output directory to `reports/allure-results`
- [x] Update `conftest.py` to use centralized screenshot path `reports/screenshots`
- [x] Update page classes (`home_page.py`, `search_results_page.py`) to use consistent screenshot paths
- [x] Clean up duplicate directories: merge or remove extra `allure-results` and `screenshots` folders
- [x] Ensure tests run from project root (`AppiumFlipkart/`) for consistency

## 2. Improve Automation Script Functionality
- [x] Add more assertions in `test_search_item.py` (e.g., verify search results, filter application, product selection)
- [x] Replace `time.sleep` with explicit waits (WebDriverWait) in page classes
- [x] Refactor error handling: reduce unnecessary screenshots, use logging for non-critical errors
- [x] Parameterize test data (brands, prices) using pytest fixtures or parametrization
- [x] Enhance Allure reporting: integrate final screenshot properly, add more attachments

## 3. Testing and Validation
- [ ] Run tests from consistent directory and verify single report directories
- [ ] Check Allure reports for completeness
- [ ] Validate improved functionality (assertions, waits)

## 4. Final Cleanup
- [ ] Remove any remaining duplicate files
- [ ] Update documentation if needed
