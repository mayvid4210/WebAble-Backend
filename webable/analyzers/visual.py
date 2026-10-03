"""Deterministic visual accessibility checks over extracted page data."""

import re

from webable.analyzers.base import Analyzer
from webable.models import (
    AffectedElement,
    AnalyzerResult,
    Finding,
    PageSnapshot,
    VisualTextSample,
)

_RGB_COLOR = re.compile(
    r"^rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)"
    r"(?:\s*[,/]\s*([\d.]+%?))?\s*\)$",
    re.IGNORECASE,
)
_HEX_COLOR = re.compile(r"^#([0-9a-f]{3,8})$", re.IGNORECASE)
_NON_CONTENT_TAGS = {
    "abbr",
    "br",
    "button",
    "code",
    "hr",
    "kbd",
    "nav",
    "samp",
    "small",
    "script",
    "style",
    "sub",
    "sup",
    "svg",
    "time",
    "path",
}
_VERY_SMALL_TEXT_PX = 10.0
_MAX_FINDINGS = 50
_WCAG_CONTRAST_REFERENCE = "wcag143"


def parse_color(value: str) -> tuple[float, float, float, float] | None:
    """Parse browser-computed rgb/rgba and common hex colors."""
    value = value.strip()
    hex_match = _HEX_COLOR.fullmatch(value)
    if hex_match:
        digits = hex_match.group(1)
        if len(digits) in {3, 4}:
            channels = [int(digit * 2, 16) for digit in digits[:3]]
            alpha = (
                int(digits[3] * 2, 16) / 255
                if len(digits) == 4
                else 1.0
            )
        elif len(digits) in {6, 8}:
            channels = [
                int(digits[index : index + 2], 16)
                for index in (0, 2, 4)
            ]
            alpha = int(digits[6:8], 16) / 255 if len(digits) == 8 else 1.0
        else:
            return None
        return (*tuple(channel / 255 for channel in channels), alpha)

    match = _RGB_COLOR.fullmatch(value)
    if not match:
        return None
    try:
        red, green, blue = (
            min(255.0, max(0.0, float(match.group(index))))
            for index in (1, 2, 3)
        )
        alpha_text = match.group(4) or "1"
        alpha = float(alpha_text.rstrip("%"))
        if alpha_text.endswith("%"):
            alpha /= 100
        alpha = min(1.0, max(0.0, alpha))
    except ValueError:
        return None
    return red / 255, green / 255, blue / 255, alpha


def relative_luminance(color: tuple[float, float, float]) -> float:
    linear = tuple(
        channel / 12.92
        if channel <= 0.04045
        else ((channel + 0.055) / 1.055) ** 2.4
        for channel in color
    )
    return (
        0.2126 * linear[0]
        + 0.7152 * linear[1]
        + 0.0722 * linear[2]
    )


def contrast_ratio(foreground: str, background: str) -> float | None:
    foreground_color = parse_color(foreground)
    background_color = parse_color(background)
    if foreground_color is None or background_color is None:
        return None
    opaque_white = (1.0, 1.0, 1.0)
    background_rgb = tuple(
        channel * background_color[3] + white * (1 - background_color[3])
        for channel, white in zip(background_color[:3], opaque_white)
    )
    foreground_rgb = tuple(
        channel * foreground_color[3] + backdrop * (1 - foreground_color[3])
        for channel, backdrop in zip(foreground_color[:3], background_rgb)
    )
    foreground_luminance = relative_luminance(foreground_rgb)
    background_luminance = relative_luminance(background_rgb)
    lighter, darker = sorted(
        (foreground_luminance, background_luminance),
        reverse=True,
    )
    return (lighter + 0.05) / (darker + 0.05)


def _is_large_text(sample: VisualTextSample) -> bool:
    if sample.font_size_px is None:
        return False
    try:
        bold = float(sample.font_weight) >= 700
    except (TypeError, ValueError):
        bold = str(sample.font_weight).lower() in {"bold", "bolder"}
    return sample.font_size_px >= (18.66 if bold else 24.0)


def _axe_contrast_targets(snapshot: PageSnapshot) -> set[str]:
    return {
        target
        for issue in snapshot.axe_scan.violations
        if issue.rule_id == "color-contrast"
        for element in issue.affected_elements
        for target in element.target
    }


def _finding(
    *,
    rule_id: str,
    title: str,
    description: str,
    sample: VisualTextSample,
    wcag_references: list[str],
    severity: str | None = "moderate",
) -> Finding:
    return Finding(
        analyzer="visual",
        rule_id=rule_id,
        title=title,
        description=description,
        severity=severity,
        category="visual",
        affected_elements=[
            AffectedElement(
                target=[sample.selector],
                html=sample.html,
                failure_summary=(
                    f"Text: {sample.text!r}; "
                    f"font size: {sample.font_size_px:g}px"
                    if sample.font_size_px is not None
                    else f"Text: {sample.text!r}"
                ),
            )
        ],
        wcag_references=wcag_references,
    )


class VisualAccessibilityAnalyzer:
    name = "visual"

    def analyze(self, snapshot: PageSnapshot) -> AnalyzerResult:
        findings: list[Finding] = []
        axe_contrast_targets = _axe_contrast_targets(snapshot)
        suppressed_contrast_findings = 0
        truncated = False

        for sample in snapshot.visual_text_samples:
            if (
                not sample.text.strip()
                or sample.tag.lower() in _NON_CONTENT_TAGS
            ):
                continue

            if len(findings) >= _MAX_FINDINGS:
                truncated = True
                break

            ratio: float | None = None
            if sample.background_color is not None:
                ratio = contrast_ratio(
                    sample.foreground_color,
                    sample.background_color,
                )

            if (
                ratio is not None
                and ratio < (3.0 if _is_large_text(sample) else 4.5)
            ):
                if sample.selector in axe_contrast_targets:
                    suppressed_contrast_findings += 1
                else:
                    findings.append(
                        _finding(
                            rule_id="visual-text-contrast",
                            title="Text may have insufficient color contrast",
                            description=(
                                f"This text has a measured contrast ratio of "
                                f"{ratio:.2f}:1. WCAG 2.1 Success Criterion 1.4.3 "
                                "requires at least 4.5:1 for normal text and "
                                "3:1 for large text."
                            ),
                            sample=sample,
                            wcag_references=[_WCAG_CONTRAST_REFERENCE],
                        )
                    )

            if (
                sample.font_size_px is not None
                and sample.font_size_px < _VERY_SMALL_TEXT_PX
            ):
                if len(findings) >= _MAX_FINDINGS:
                    truncated = True
                    break
                findings.append(
                    _finding(
                        rule_id="visual-very-small-text",
                        title="Text is rendered at a very small size",
                        description=(
                            f"This visible text is rendered at "
                            f"{sample.font_size_px:g}px. This is a readability "
                            "signal rather than a standalone WCAG failure. "
                            "Review its purpose and whether it can be made "
                            "easier to read."
                        ),
                        sample=sample,
                        wcag_references=[],
                        severity=None,
                    )
                )

        return AnalyzerResult(
            analyzer=self.name,
            findings=findings,
            metadata={
                "text_samples_inspected": len(snapshot.visual_text_samples),
                "contrast_findings_suppressed_by_axe": (
                    suppressed_contrast_findings
                ),
                "findings_truncated": int(truncated),
            },
        )


assert isinstance(VisualAccessibilityAnalyzer(), Analyzer)
