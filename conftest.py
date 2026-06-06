# conftest.py
# Pytest configuration for Playwright-based tests
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="module")
def create_page_instance():
    """
    Page Instance to open a Chromium blank page for tests.
    Scope: module (one browser page per test module)
    """
    pl = sync_playwright().start()
    browser = pl.chromium.launch(headless=False, slow_mo=500, args=["--start-maximized"])
    context = browser.new_context(no_viewport=True)
    page = context.new_page()
    yield page
    page.close()
    context.close()
    browser.close()
    pl.stop()
