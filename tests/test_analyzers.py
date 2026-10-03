import unittest
from dataclasses import asdict
from datetime import datetime, timezone
from unittest.mock import Mock, patch

from webable.analyzers.axe import (
    AxeAccessibilityAnalyzer,
    collect_axe_scan,
)
from webable.analyzers.base import Analyzer
from webable.analyzers.page_structure import PageStructureAnalyzer
from webable.models import (
    AffectedElement,
    AnalyzerResult,
    AxeAffectedElementData,
    AxeIssueData,
    AxeScanData,
    Finding,
    PageSnapshot,
    PageStructure,
    PassedCheck,
    ScanMetadata,
)
from webable.pipeline import ANALYZERS, build_report, run_analyzers
from webable.snapshot import create_page_snapshot


def make_snapshot() -> PageSnapshot:
    structure = PageStructure(
        title="Example",
        final_url="https://example.com/",
        links=1,
        images=2,
        buttons=3,
        forms=4,
        inputs=5,
        headings=6,
        images_without_alt=7,
    )
    return PageSnapshot(
        requested_url="https://example.com",
        final_url="https://example.com/",
        title="Example",
        structure=structure,
        viewport={"width": 1440, "height": 900},
        axe_scan=AxeScanData(
            violations=[
                AxeIssueData(
                    impact="serious",
                    help="Image needs alternative text",
                    description="Provide a text alternative.",
                    rule_id="image-alt",
                    tags=["wcag111", "wcag2a"],
                    affected_elements=[
                        AxeAffectedElementData(
                            target=["img.hero"],
                            html='<img class="hero">',
                            failure_summary="Add an alt attribute.",
                        )
                    ],
                )
            ],
            passes=[PassedCheck(help="Document has a title")],
        ),
    )


class AnalyzerContractTests(unittest.TestCase):
    def test_current_analyzers_implement_shared_contract(self) -> None:
        self.assertIsInstance(AxeAccessibilityAnalyzer(), Analyzer)
        self.assertIsInstance(PageStructureAnalyzer(), Analyzer)

    def test_analyzer_results_include_identity_and_structured_lists(self) -> None:
        result = PageStructureAnalyzer().analyze(make_snapshot())

        self.assertEqual(result.analyzer, "page_structure")
        self.assertEqual(result.findings, [])
        self.assertEqual(result.passed_checks, [])
        self.assertEqual(result.page_structure, make_snapshot().structure)


class FindingAndSnapshotTests(unittest.TestCase):
    def test_finding_contains_shared_and_axe_evidence_fields(self) -> None:
        finding = AxeAccessibilityAnalyzer().analyze(make_snapshot()).findings[0]

        self.assertEqual(finding.analyzer, "axe")
        self.assertEqual(finding.rule_id, "image-alt")
        self.assertEqual(finding.title, "Image needs alternative text")
        self.assertEqual(finding.severity, "serious")
        self.assertEqual(finding.category, "technical_accessibility")
        self.assertEqual(finding.wcag_references, ["wcag111", "wcag2a"])
        self.assertEqual(finding.affected_elements[0].target, ["img.hero"])
        self.assertEqual(finding.affected_elements[0].html, '<img class="hero">')
        self.assertEqual(finding.impact, "serious")
        self.assertEqual(finding.help, finding.title)

    def test_snapshot_is_structured_and_contains_no_browser_objects(self) -> None:
        snapshot = make_snapshot()
        serialized = asdict(snapshot)

        self.assertEqual(snapshot.requested_url, "https://example.com")
        self.assertEqual(snapshot.final_url, "https://example.com/")
        self.assertEqual(snapshot.title, "Example")
        self.assertEqual(snapshot.structure.elements_scanned, 11)
        self.assertEqual(snapshot.viewport, {"width": 1440, "height": 900})
        self.assertEqual(serialized["axe_scan"]["violations"][0]["rule_id"], "image-alt")
        self.assertNotIn("page", serialized)
        self.assertNotIn("browser", serialized)

    @patch("webable.snapshot.collect_axe_scan")
    @patch("webable.snapshot.extract_page_structure")
    def test_snapshot_factory_extracts_and_scans_without_retaining_page(
        self,
        extract_structure: Mock,
        collect_axe: Mock,
    ) -> None:
        structure = make_snapshot().structure
        axe_scan = make_snapshot().axe_scan
        extract_structure.return_value = structure
        collect_axe.return_value = axe_scan
        page = Mock()
        page.url = "https://example.com/"
        stages: list[str] = []

        snapshot = create_page_snapshot(
            page,
            "https://example.com",
            on_progress=stages.append,
        )

        self.assertEqual(snapshot.structure, structure)
        self.assertEqual(snapshot.axe_scan, axe_scan)
        self.assertEqual(stages, ["extracting", "scanning"])
        extract_structure.assert_called_once_with(page)
        collect_axe.assert_called_once_with(page)


class AxeAnalyzerTests(unittest.TestCase):
    @patch("webable.analyzers.axe.Axe")
    def test_live_page_collection_is_normalized_to_data(
        self,
        axe_type: Mock,
    ) -> None:
        page = Mock()
        axe_type.return_value.run.return_value.response = {
            "violations": [
                {
                    "impact": "moderate",
                    "help": "Rule title",
                    "description": "Rule description",
                    "id": "test-rule",
                    "tags": ["wcag111", "best-practice"],
                    "nodes": [
                        {
                            "target": [["main", "img"]],
                            "html": "<img>",
                            "failureSummary": "Add alt text.",
                        }
                    ],
                }
            ],
            "passes": [{"help": "Landmarks exist"}],
        }

        scan = collect_axe_scan(page)

        axe_type.return_value.run.assert_called_once_with(page)
        self.assertEqual(scan.violations[0].rule_id, "test-rule")
        self.assertEqual(scan.violations[0].affected_elements[0].target, ["main", "img"])
        self.assertEqual(scan.passes[0].help, "Landmarks exist")

    def test_analyzer_maps_axe_data_without_changing_finding_text(self) -> None:
        result = AxeAccessibilityAnalyzer().analyze(make_snapshot())

        self.assertEqual(result.analyzer, "axe")
        self.assertEqual(len(result.findings), 1)
        self.assertEqual(result.findings[0].description, "Provide a text alternative.")
        self.assertEqual(result.passed_checks[0].help, "Document has a title")


class AnalyzerPipelineTests(unittest.TestCase):
    def test_pipeline_runs_and_combines_registered_analyzer_results(self) -> None:
        snapshot = make_snapshot()
        results = run_analyzers(snapshot)
        metadata = ScanMetadata(
            started_at=datetime(2026, 10, 3, tzinfo=timezone.utc),
            duration_seconds=0.5,
            browser="Chromium",
            viewport=snapshot.viewport,
        )

        report = build_report(snapshot, results, metadata)

        self.assertEqual(
            [result.analyzer for result in results],
            ["axe", "page_structure", "visual"],
        )
        self.assertEqual(report.findings, results[0].findings)
        self.assertEqual(report.violations, report.findings)
        self.assertEqual(report.passes, results[0].passed_checks)
        self.assertEqual(report.page.images_without_alt, 7)
        self.assertEqual(report.score, 93)

    def test_future_analyzer_can_be_added_without_scoring_changes(self) -> None:
        class ExampleFutureAnalyzer:
            name = "example_future"

            def analyze(self, _snapshot: PageSnapshot) -> AnalyzerResult:
                _ = _snapshot
                return AnalyzerResult(
                    analyzer=self.name,
                    findings=[
                        Finding(
                            analyzer=self.name,
                            rule_id="future-check",
                            title="Example future finding",
                            description="Structured finding.",
                            severity="minor",
                            category="technical_accessibility",
                            affected_elements=[
                                AffectedElement(target=["main"])
                            ],
                        )
                    ],
                )

        analyzer = ExampleFutureAnalyzer()
        self.assertIsInstance(analyzer, Analyzer)
        snapshot = make_snapshot()
        results = run_analyzers(snapshot, (*ANALYZERS, analyzer))
        metadata = ScanMetadata(
            started_at=datetime(2026, 10, 3, tzinfo=timezone.utc),
            duration_seconds=0.5,
            browser="Chromium",
            viewport=snapshot.viewport,
        )

        report = build_report(snapshot, results, metadata)

        self.assertEqual(len(report.findings), 2)
        self.assertEqual(report.findings[-1].analyzer, "example_future")
        self.assertEqual(report.score, 91)
