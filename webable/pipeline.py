"""Run analyzers over a page snapshot and assemble their results."""

from collections.abc import Iterable, Sequence

from webable.analyzers.axe import AxeAccessibilityAnalyzer
from webable.analyzers.base import Analyzer
from webable.analyzers.page_structure import PageStructureAnalyzer
from webable.analyzers.visual import VisualAccessibilityAnalyzer
from webable.models import (
    AnalyzerResult,
    AuditReport,
    PageSnapshot,
    ScanMetadata,
)
from webable.scoring import calculate_score

ANALYZERS: tuple[Analyzer, ...] = (
    AxeAccessibilityAnalyzer(),
    PageStructureAnalyzer(),
    VisualAccessibilityAnalyzer(),
)


def run_analyzers(
    snapshot: PageSnapshot,
    analyzers: Sequence[Analyzer] = ANALYZERS,
) -> list[AnalyzerResult]:
    return [analyzer.analyze(snapshot) for analyzer in analyzers]


def build_report(
    snapshot: PageSnapshot,
    results: Iterable[AnalyzerResult],
    metadata: ScanMetadata,
) -> AuditReport:
    analyzer_results = list(results)
    findings = [
        finding
        for result in analyzer_results
        for finding in result.findings
    ]
    passed_checks = [
        check
        for result in analyzer_results
        for check in result.passed_checks
    ]
    page_structure = next(
        (
            result.page_structure
            for result in analyzer_results
            if result.page_structure is not None
        ),
        snapshot.structure,
    )
    score, severity = calculate_score(findings)

    return AuditReport(
        url=snapshot.requested_url,
        page=page_structure,
        findings=findings,
        passes=passed_checks,
        severity=severity,
        score=score,
        metadata=metadata,
    )
