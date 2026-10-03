import unittest

from fastapi.testclient import TestClient

from webable.api.app import app


class PublicWebsiteIntegrationTest(unittest.TestCase):
    def test_analysis_api_scans_example_domain(self) -> None:
        with TestClient(app) as client:
            response = client.post(
                "/api/analyze",
                json={"url": "https://example.com"},
            )

        self.assertEqual(response.status_code, 200, response.text)
        report = response.json()["report"]
        self.assertEqual(report["url"], "https://example.com")
        self.assertEqual(report["final_url"], "https://example.com/")
        self.assertEqual(report["title"], "Example Domain")
        self.assertGreaterEqual(report["score"], 0)
        self.assertLessEqual(report["score"], 100)
        self.assertIsInstance(report["findings"], list)
        self.assertIsInstance(report["passed_checks"], list)
        self.assertEqual(report["scan_metadata"]["browser"], "Chromium")
