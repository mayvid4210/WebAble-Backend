"""Playwright page loading and browser lifecycle management."""

from contextlib import contextmanager
from collections.abc import Generator

from playwright.sync_api import Page, sync_playwright

from webable.config import (
    PAGE_LOAD_TIMEOUT_MS,
    PAGE_LOAD_WAIT_UNTIL,
    VIEWPORT,
)


@contextmanager
def loaded_page(url: str) -> Generator[Page, None, None]:
    """Open a Chromium page and always release the browser on exit."""
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page(viewport=VIEWPORT)
            page.goto(
                url,
                wait_until=PAGE_LOAD_WAIT_UNTIL,
                timeout=PAGE_LOAD_TIMEOUT_MS,
            )
            yield page
        finally:
            browser.close()
