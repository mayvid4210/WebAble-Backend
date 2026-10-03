"""Build a compact, Playwright-free representation of a loaded page."""

from collections.abc import Callable

from playwright.sync_api import Page

from webable.analyzers.axe import collect_axe_scan
from webable.config import VIEWPORT
from webable.extraction import (
    extract_page_structure,
    extract_visual_text_samples,
)
from webable.models import PageSnapshot


def create_page_snapshot(
    page: Page,
    requested_url: str,
    on_progress: Callable[[str], None] | None = None,
) -> PageSnapshot:
    if on_progress is not None:
        on_progress("extracting")
    structure = extract_page_structure(page)
    visual_text_samples = extract_visual_text_samples(page)
    if on_progress is not None:
        on_progress("scanning")
    axe_scan = collect_axe_scan(page)

    return PageSnapshot(
        requested_url=requested_url,
        final_url=page.url,
        title=structure.title,
        structure=structure,
        viewport=dict(VIEWPORT),
        axe_scan=axe_scan,
        visual_text_samples=visual_text_samples,
    )
