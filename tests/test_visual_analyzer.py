import unittest
from unittest.mock import Mock

from webable.analyzers.axe import AxeAccessibilityAnalyzer
from webable.analyzers.page_structure import PageStructureAnalyzer
from webable.analyzers.visual import (
    VisualAccessibilityAnalyzer,
    contrast_ratio,
    parse_color,
)
from webable.extraction import extract_visual_text_samples
from webable.models import (
    AxeAffectedElementData,
    AxeIssueData,
    AxeScanData,
    PageSnapshot,
    PageStructure,
    VisualTextSample,
)
from webable.pipeline import ANALYZERS
from webable.scoring import calculate_score


def make_snapshot(
    samples: list[VisualTextSample],
    axe_violations: list[AxeIssueData] | None = None,
) -> PageSnapshot:
    structure = PageStructure(
        title="Fixture",
        final_url="https://fixture.test/",
        links=0,
        images=0,
        buttons=0,
        forms=0,
        inputs=0,
        headings=1,
        images_without_alt=0,
    )
    return PageSnapshot(
        requested_url="https://fixture.test/",
        final_url="https://fixture.test/",
        title="Fixture",
        structure=structure,
        viewport={"width": 1440, "height": 900},
        axe_scan=AxeScanData(violations=axe_violations or []),
        visual_text_samples=samples,
    )


def make_sample(
    *,
    text: str = "Example content",
    selector: str = "p",
    foreground: str = "rgb(0, 0, 0)",
    background: str | None = "rgb(255, 255, 255)",
    font_size: float | None = 16,
    weight: int | str = 400,
    tag: str = "p",
) -> VisualTextSample:
    return VisualTextSample(
        selector=selector,
        ancestor_selectors=["body"],
        text=text,
        tag=tag,
        foreground_color=foreground,
        background_color=background,
        font_size_px=font_size,
        font_weight=weight,
        html=f"<{tag}>{text}</{tag}>",
    )


class ContrastCalculationTests(unittest.TestCase):
    def test_wcag_contrast_ratio_for_black_and_white(self) -> None:
        self.assertAlmostEqual(
            contrast_ratio("#000", "#fff") or 0,
            21.0,
            places=5,
        )

    def test_common_rgb_rgba_and_hex_colors_parse(self) -> None:
        self.assertEqual(
            parse_color("#abc"),
            (170 / 255, 187 / 255, 204 / 255, 1.0),
        )
        self.assertEqual(
            parse_color("rgb(255, 0, 0)"),
            (1.0, 0.0, 0.0, 1.0),
        )
        self.assertEqual(
            parse_color("rgba(0, 0, 0, 40%)"),
            (0.0, 0.0, 0.0, 0.4),
        )
        self.assertAlmostEqual(
            contrast_ratio("rgba(0, 0, 0, 0.5)", "rgb(255, 255, 255)") or 0,
            3.98,
            places=2,
        )

    def test_passes_normal_and_large_text_contrast_thresholds(self) -> None:
        normal = make_sample(foreground="rgb(118, 118, 118)")
        large = make_sample(
            foreground="rgb(145, 145, 145)",
            font_size=24,
        )

        result = VisualAccessibilityAnalyzer().analyze(
            make_snapshot([normal, large])
        )

        self.assertEqual(result.findings, [])

    def test_fails_insufficient_normal_text_contrast(self) -> None:
        result = VisualAccessibilityAnalyzer().analyze(
            make_snapshot([make_sample(foreground="rgb(160, 160, 160)")])
        )

        self.assertEqual(len(result.findings), 1)
        self.assertEqual(result.findings[0].rule_id, "visual-text-contrast")
        self.assertIn("2.61:1", result.findings[0].description)
        self.assertEqual(result.findings[0].wcag_references, ["wcag143"])

    def test_indeterminate_background_does_not_produce_contrast_finding(self) -> None:
        result = VisualAccessibilityAnalyzer().analyze(
            make_snapshot(
                [
                    make_sample(
                        foreground="rgb(255, 255, 255)",
                        background=None,
                    )
                ]
            )
        )

        self.assertEqual(result.findings, [])

    def test_small_text_finding_includes_actual_font_size_and_selector(self) -> None:
        result = VisualAccessibilityAnalyzer().analyze(
            make_snapshot(
                [
                    make_sample(
                        text="Tiny legal copy",
                        selector="footer .legal",
                        font_size=9,
                    )
                ]
            )
        )

        self.assertEqual(len(result.findings), 1)
        finding = result.findings[0]
        self.assertEqual(finding.rule_id, "visual-very-small-text")
        self.assertEqual(finding.category, "visual")
        self.assertIsNone(finding.severity)
        self.assertEqual(finding.wcag_references, [])
        self.assertEqual(finding.affected_elements[0].target, ["footer .legal"])
        self.assertIn("9px", finding.affected_elements[0].failure_summary or "")
        self.assertIn("readability signal", finding.description)

    def test_small_text_observation_does_not_change_existing_score(self) -> None:
        result = VisualAccessibilityAnalyzer().analyze(
            make_snapshot([make_sample(font_size=9)])
        )

        self.assertEqual(calculate_score([]), calculate_score(result.findings))

    def test_non_content_sample_is_ignored(self) -> None:
        result = VisualAccessibilityAnalyzer().analyze(
            make_snapshot(
                [
                    make_sample(
                        text="",
                        tag="svg",
                        foreground="rgb(255, 255, 255)",
                    )
                ]
            )
        )

        self.assertEqual(result.findings, [])

    def test_existing_axe_contrast_violation_suppresses_duplicate(self) -> None:
        axe_finding = AxeIssueData(
            impact="serious",
            help="Ensure the contrast between foreground and background colors meets WCAG 2 AA minimum contrast ratio thresholds",
            description="Axe reports insufficient contrast.",
            rule_id="color-contrast",
            affected_elements=[AxeAffectedElementData(target=["p"])],
        )

        result = VisualAccessibilityAnalyzer().analyze(
            make_snapshot(
                [
                    make_sample(foreground="rgb(160, 160, 160)"),
                    make_sample(
                        text="Other small text",
                        selector="small",
                        font_size=9,
                    ),
                ],
                axe_violations=[axe_finding],
            )
        )

        self.assertEqual([finding.rule_id for finding in result.findings], ["visual-very-small-text"])
        self.assertEqual(result.metadata["contrast_findings_suppressed_by_axe"], 1)

    def test_axe_contrast_finding_does_not_suppress_other_elements(self) -> None:
        axe_finding = AxeIssueData(
            impact="serious",
            help="Contrast",
            description="Axe reports a different element.",
            rule_id="color-contrast",
            affected_elements=[AxeAffectedElementData(target=["#other"])],
        )

        result = VisualAccessibilityAnalyzer().analyze(
            make_snapshot(
                [make_sample(foreground="rgb(160, 160, 160)")],
                axe_violations=[axe_finding],
            )
        )

        self.assertEqual([finding.rule_id for finding in result.findings], ["visual-text-contrast"])
        self.assertEqual(result.metadata["contrast_findings_suppressed_by_axe"], 0)


class VisualSnapshotAndPipelineTests(unittest.TestCase):
    def test_visual_sample_extraction_is_bounded_and_structured(self) -> None:
        page = Mock()
        page.evaluate.return_value = [
            {
                "selector": "body > p",
                "ancestor_selectors": ["body"],
                "text": "Visible text",
                "tag": "p",
                "foreground_color": "rgb(0, 0, 0)",
                "background_color": "rgb(255, 255, 255)",
                "font_size_px": 14,
                "font_weight": "400",
                "html": "<p>Visible text</p>",
            },
            {"selector": "invalid"},
        ]

        samples = extract_visual_text_samples(page)

        self.assertEqual(len(samples), 1)
        self.assertEqual(samples[0].text, "Visible text")
        self.assertEqual(samples[0].font_size_px, 14.0)
        self.assertEqual(samples[0].background_color, "rgb(255, 255, 255)")
        self.assertEqual(samples[0].selector, "body > p")

    def test_analyzer_result_has_stable_name_and_findings(self) -> None:
        result = VisualAccessibilityAnalyzer().analyze(
            make_snapshot([make_sample(foreground="rgb(160, 160, 160)")])
        )

        self.assertEqual(result.analyzer, "visual")
        self.assertEqual(len(result.findings), 1)
        self.assertEqual(result.findings[0].analyzer, "visual")
        self.assertEqual(result.findings[0].category, "visual")
        self.assertEqual(result.metadata["text_samples_inspected"], 1)

    def test_pipeline_registers_visual_without_replacing_existing_analyzers(self) -> None:
        analyzers_by_name = {analyzer.name: analyzer for analyzer in ANALYZERS}

        self.assertIsInstance(analyzers_by_name["axe"], AxeAccessibilityAnalyzer)
        self.assertIsInstance(
            analyzers_by_name["page_structure"],
            PageStructureAnalyzer,
        )
        self.assertIsInstance(
            analyzers_by_name["visual"],
            VisualAccessibilityAnalyzer,
        )
