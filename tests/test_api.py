import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from webable.api.app import app
from webable.models import (
    AffectedElement,
    AuditReport,
    Finding,
    PageStructure,
    PassedCheck,
    ScanMetadata,
    SeverityBreakdown,
)


def sample_report() -> AuditReport:
    return AuditReport(
        url="https://example.com",
        page=PageStructure(
            title="Example Domain",
            final_url="https://example.com/",
            links=1,
            images=2,
            buttons=3,
            forms=1,
            inputs=2,
            headings=4,
            images_without_alt=1,
        ),
        findings=[
            Finding(
                analyzer="axe",
                rule_id="image-alt",
                title="Images must have alternate text",
                description="Image elements need text alternatives.",
                severity="serious",
                category="technical_accessibility",
                wcag_references=["wcag111"],
                affected_elements=[
                    AffectedElement(
                        target=["img.hero"],
                        html='<img class="hero" src="hero.png">',
                        failure_summary="Add an alt attribute.",
                    )
                ],
            )
        ],
        passes=[PassedCheck(help="Document has a title")],
        severity=SeverityBreakdown(serious=1),
        score=93,
        metadata=ScanMetadata(
            started_at=datetime(2026, 10, 3, tzinfo=timezone.utc),
            duration_seconds=1.25,
            browser="Chromium",
            viewport={"width": 1440, "height": 900},
        ),
    )


class ApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_health_check(self) -> None:
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    @patch("webable.api.routes.analysis.analyze_website")
    def test_analyze_returns_report_fields(
        self,
        analyze_website: MagicMock,
    ) -> None:
        analyze_website.return_value = sample_report()

        response = self.client.post(
            "/api/analyze",
            json={"url": "example.com"},
        )

        self.assertEqual(response.status_code, 200)
        analyze_website.assert_called_once_with("https://example.com")
        report = response.json()["report"]
        self.assertEqual(report["url"], "https://example.com")
        self.assertEqual(report["final_url"], "https://example.com/")
        self.assertEqual(report["title"], "Example Domain")
        self.assertEqual(report["score"], 93)
        self.assertEqual(report["severity_counts"]["serious"], 1)
        self.assertEqual(report["page_structure"]["images_without_alt"], 1)
        self.assertEqual(report["page_structure"]["elements_scanned"], 8)
        self.assertEqual(report["findings"][0]["rule_id"], "image-alt")
        self.assertEqual(
            report["findings"][0]["wcag_references"],
            ["wcag111"],
        )
        self.assertEqual(
            report["findings"][0]["affected_elements"][0]["target"],
            ["img.hero"],
        )
        self.assertEqual(
            report["passed_checks"][0]["title"],
            "Document has a title",
        )
        self.assertEqual(report["scan_metadata"]["browser"], "Chromium")

    @patch("webable.api.routes.analysis.analyze_website")
    def test_invalid_url_returns_400_without_scanning(
        self,
        analyze_website: MagicMock,
    ) -> None:
        response = self.client.post(
            "/api/analyze",
            json={"url": "javascript:alert(1)"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {"detail": "Enter a valid HTTP or HTTPS URL."},
        )
        analyze_website.assert_not_called()

    @patch("webable.api.routes.analysis.analyze_website")
    def test_malformed_host_returns_400(
        self,
        analyze_website: MagicMock,
    ) -> None:
        response = self.client.post(
            "/api/analyze",
            json={"url": "https://not a valid host"},
        )

        self.assertEqual(response.status_code, 400)
        analyze_website.assert_not_called()

    @patch("webable.api.routes.analysis.analyze_website")
    def test_analysis_failure_returns_safe_error(
        self,
        analyze_website: MagicMock,
    ) -> None:
        analyze_website.side_effect = RuntimeError("private implementation detail")

        response = self.client.post(
            "/api/analyze",
            json={"url": "https://example.com"},
        )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json(),
            {"detail": "The analysis could not be completed."},
        )
        self.assertNotIn("private implementation detail", response.text)

    @patch("webable.api.routes.analysis.analyze_website")
    def test_browser_timeout_returns_gateway_timeout(
        self,
        analyze_website: MagicMock,
    ) -> None:
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

        analyze_website.side_effect = PlaywrightTimeoutError("internal timeout")

        response = self.client.post(
            "/api/analyze",
            json={"url": "https://example.com"},
        )

        self.assertEqual(response.status_code, 504)
        self.assertEqual(
            response.json(),
            {"detail": "The website took too long to respond."},
        )

    @patch("webable.api.routes.analysis.analyze_website")
    def test_browser_failure_returns_bad_gateway(
        self,
        analyze_website: MagicMock,
    ) -> None:
        from playwright.sync_api import Error as PlaywrightError

        analyze_website.side_effect = PlaywrightError("internal browser error")

        response = self.client.post(
            "/api/analyze",
            json={"url": "https://example.com"},
        )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(
            response.json(),
            {"detail": "The website could not be loaded for analysis."},
        )

    def test_cors_allows_vite_development_origin(self) -> None:
        response = self.client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers["access-control-allow-origin"],
            "http://localhost:5173",
        )
