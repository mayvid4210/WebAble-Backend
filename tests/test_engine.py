import unittest

from webable.models import Finding
from webable.scoring import calculate_score
from webable.utils import normalize_url


class ScoringTests(unittest.TestCase):
    def test_existing_penalties_and_severity_counts(self) -> None:
        issues = [
            Finding("test", "critical", "Critical", "", "critical", "test"),
            Finding("test", "serious", "Serious", "", "serious", "test"),
            Finding("test", "moderate", "Moderate", "", "moderate", "test"),
            Finding("test", "minor", "Minor", "", "minor", "test"),
            Finding("test", "unknown", "Unknown", "", "unknown", "test"),
        ]

        score, severity = calculate_score(issues)

        self.assertEqual(score, 77)
        self.assertEqual(
            (
                severity.critical,
                severity.serious,
                severity.moderate,
                severity.minor,
            ),
            (1, 1, 1, 1),
        )

    def test_score_does_not_fall_below_zero(self) -> None:
        issues = [
            Finding("test", "critical", "Critical", "", "critical", "test")
            for _ in range(11)
        ]

        score, _ = calculate_score(issues)

        self.assertEqual(score, 0)


class UrlNormalizationTests(unittest.TestCase):
    def test_adds_https_when_scheme_is_missing(self) -> None:
        self.assertEqual(
            normalize_url("example.com"),
            "https://example.com",
        )

    def test_preserves_existing_http_scheme(self) -> None:
        self.assertEqual(
            normalize_url("http://example.com"),
            "http://example.com",
        )
