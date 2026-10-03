"""Severity counts and the existing penalty-based score calculation."""

from collections.abc import Iterable

from webable.config import IMPACT_PENALTIES, MAX_SCORE
from webable.models import Finding, SeverityBreakdown


def calculate_score(
    findings: Iterable[Finding],
) -> tuple[int, SeverityBreakdown]:
    severity = SeverityBreakdown()
    penalty = 0

    for finding in findings:
        impact = finding.severity
        if impact == "critical":
            severity.critical += 1
        elif impact == "serious":
            severity.serious += 1
        elif impact == "moderate":
            severity.moderate += 1
        elif impact == "minor":
            severity.minor += 1

        penalty += IMPACT_PENALTIES.get(impact, 0)

    return max(0, MAX_SCORE - penalty), severity
