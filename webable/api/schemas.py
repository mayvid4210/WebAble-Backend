"""Typed JSON request and response models for the WebAble API."""

from datetime import datetime
from urllib.parse import urlsplit

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, TypeAdapter, field_validator

from webable.models import AuditReport

_HTTP_URL_ADAPTER = TypeAdapter(AnyHttpUrl)


class AnalysisRequest(BaseModel):
    url: str = Field(min_length=1, max_length=2048)

    @field_validator("url")
    @classmethod
    def validate_and_normalize_url(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("URL must not be empty.")

        if "://" not in value:
            value = f"https://{value}"

        try:
            parsed = urlsplit(value)
            _HTTP_URL_ADAPTER.validate_python(value)
        except ValueError as error:
            raise ValueError("Enter a valid HTTP or HTTPS URL.") from error

        if (
            parsed.scheme.lower() not in {"http", "https"}
            or parsed.username is not None
            or parsed.password is not None
        ):
            raise ValueError("Enter a valid HTTP or HTTPS URL.")

        return value


class SeverityCountsResponse(BaseModel):
    critical: int
    serious: int
    moderate: int
    minor: int


class PageStructureResponse(BaseModel):
    links: int
    images: int
    buttons: int
    forms: int
    inputs: int
    headings: int
    images_without_alt: int
    elements_scanned: int


class AffectedElementResponse(BaseModel):
    target: list[str]
    html: str
    failure_summary: str | None


class FindingResponse(BaseModel):
    impact: str | None
    title: str
    description: str
    rule_id: str
    wcag_references: list[str]
    affected_elements: list[AffectedElementResponse]


class PassedCheckResponse(BaseModel):
    title: str


class ViewportResponse(BaseModel):
    width: int
    height: int


class ScanMetadataResponse(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)

    started_at: datetime
    duration_seconds: float = Field(ge=0)
    browser: str
    viewport: ViewportResponse


class AuditReportResponse(BaseModel):
    url: str
    final_url: str
    title: str
    score: int = Field(ge=0, le=100)
    severity_counts: SeverityCountsResponse
    page_structure: PageStructureResponse
    findings: list[FindingResponse]
    passed_checks: list[PassedCheckResponse]
    scan_metadata: ScanMetadataResponse

    @classmethod
    def from_audit_report(cls, report: AuditReport) -> "AuditReportResponse":
        return cls(
            url=report.url,
            final_url=report.page.final_url,
            title=report.page.title,
            score=report.score,
            severity_counts=SeverityCountsResponse(
                critical=report.severity.critical,
                serious=report.severity.serious,
                moderate=report.severity.moderate,
                minor=report.severity.minor,
            ),
            page_structure=PageStructureResponse(
                links=report.page.links,
                images=report.page.images,
                buttons=report.page.buttons,
                forms=report.page.forms,
                inputs=report.page.inputs,
                headings=report.page.headings,
                images_without_alt=report.page.images_without_alt,
                elements_scanned=report.page.elements_scanned,
            ),
            findings=[
                FindingResponse(
                    impact=issue.impact,
                    title=issue.help,
                    description=issue.description,
                    rule_id=issue.rule_id,
                    wcag_references=issue.wcag_references,
                    affected_elements=[
                        AffectedElementResponse(
                            target=element.target,
                            html=element.html,
                            failure_summary=element.failure_summary,
                        )
                        for element in issue.affected_elements
                    ],
                )
                for issue in report.violations
            ],
            passed_checks=[
                PassedCheckResponse(title=check.help)
                for check in report.passes
            ],
            scan_metadata=ScanMetadataResponse(
                started_at=report.metadata.started_at,
                duration_seconds=report.metadata.duration_seconds,
                browser=report.metadata.browser,
                viewport=ViewportResponse(
                    width=report.metadata.viewport["width"],
                    height=report.metadata.viewport["height"],
                ),
            ),
        )


class AnalyzeResponse(BaseModel):
    report: AuditReportResponse


class HealthResponse(BaseModel):
    status: str
