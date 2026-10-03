"""Orchestration for the existing single-page accessibility audit."""

from collections.abc import Callable
from datetime import datetime, timezone
from time import perf_counter

from webable.browser import loaded_page
from webable.config import VIEWPORT
from webable.models import AuditReport, ScanMetadata
from webable.pipeline import build_report, run_analyzers
from webable.snapshot import create_page_snapshot
from webable.utils import normalize_url

ProgressCallback = Callable[[str], None]


def analyze_website(
    url: str,
    on_progress: ProgressCallback | None = None,
) -> AuditReport:
    """Analyze one page and return a framework-independent audit report."""
    started_at = datetime.now(timezone.utc)
    started = perf_counter()
    normalized_url = normalize_url(url)

    _report_progress(on_progress, "opening")
    with loaded_page(normalized_url) as page:
        snapshot = create_page_snapshot(
            page,
            normalized_url,
            on_progress=on_progress,
        )
        results = run_analyzers(snapshot)

        _report_progress(on_progress, "reporting")

    metadata = ScanMetadata(
        started_at=started_at,
        duration_seconds=perf_counter() - started,
        browser="Chromium",
        viewport=dict(VIEWPORT),
    )
    return build_report(snapshot, results, metadata)


def run_audit(
    url: str,
    on_progress: ProgressCallback | None = None,
) -> AuditReport:
    """Backward-compatible alias for the legacy Streamlit UI."""
    return analyze_website(url, on_progress=on_progress)


def _report_progress(
    callback: ProgressCallback | None,
    stage: str,
) -> None:
    if callback is not None:
        callback(stage)
