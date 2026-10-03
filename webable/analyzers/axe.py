"""Axe Playwright integration and conversion to WebAble's data models."""

from collections.abc import Mapping
from typing import Any

from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import Page

from webable.models import (
    AffectedElement,
    AnalyzerResult,
    AxeAffectedElementData,
    AxeIssueData,
    AxeScanData,
    Finding,
    PageSnapshot,
    PassedCheck,
)


def _as_text(value: Any, default: str = "") -> str:
    return value if isinstance(value, str) else default


def collect_axe_scan(page: Page) -> AxeScanData:
    """Run axe on the live page and retain only structured result data."""
    response = Axe().run(page).response
    return AxeScanData(
        violations=[
            _make_issue(issue)
            for issue in response["violations"]
        ],
        passes=[
            PassedCheck(help=_as_text(check.get("help"), "Passed check"))
            for check in response["passes"]
        ],
    )


def _make_issue(raw_issue: Mapping[str, Any]) -> AxeIssueData:
    raw_nodes = raw_issue.get("nodes", [])
    raw_tags = raw_issue.get("tags", [])
    nodes = [
        AxeAffectedElementData(
            target=_as_string_list(node.get("target", [])),
            html=_as_text(node.get("html")),
            failure_summary=(
                _as_text(node.get("failureSummary"))
                if isinstance(node.get("failureSummary"), str)
                else None
            ),
        )
        for node in raw_nodes
    ]
    tags = [tag for tag in raw_tags if isinstance(tag, str)]
    impact = raw_issue.get("impact")

    return AxeIssueData(
        impact=impact if isinstance(impact, str) else None,
        help=_as_text(raw_issue.get("help"), "Accessibility issue"),
        description=_as_text(raw_issue.get("description")),
        rule_id=_as_text(raw_issue.get("id")),
        tags=tags,
        affected_elements=nodes,
    )


def _as_string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for entry in value for item in _as_string_list(entry)]
    return []


class AxeAccessibilityAnalyzer:
    name = "axe"

    def analyze(self, snapshot: PageSnapshot) -> AnalyzerResult:
        findings = [
            Finding(
                analyzer=self.name,
                rule_id=issue.rule_id,
                title=issue.help,
                description=issue.description,
                severity=issue.impact,
                category="technical_accessibility",
                affected_elements=[
                    AffectedElement(
                        target=element.target,
                        html=element.html,
                        failure_summary=element.failure_summary,
                    )
                    for element in issue.affected_elements
                ],
                wcag_references=[
                    tag
                    for tag in issue.tags
                    if tag.startswith("wcag")
                ],
            )
            for issue in snapshot.axe_scan.violations
        ]
        return AnalyzerResult(
            analyzer=self.name,
            findings=findings,
            passed_checks=snapshot.axe_scan.passes,
        )
