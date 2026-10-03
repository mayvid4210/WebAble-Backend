"""Structured data exchanged by WebAble's analysis pipeline."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class PageStructure:
    title: str
    final_url: str
    links: int
    images: int
    buttons: int
    forms: int
    inputs: int
    headings: int
    images_without_alt: int

    @property
    def elements_scanned(self) -> int:
        return self.links + self.images + self.buttons + self.inputs


@dataclass
class VisualTextSample:
    selector: str
    ancestor_selectors: list[str]
    text: str
    tag: str
    foreground_color: str
    background_color: str | None
    font_size_px: float | None
    font_weight: int | str
    html: str


@dataclass
class AffectedElement:
    target: list[str] = field(default_factory=list)
    html: str = ""
    failure_summary: str | None = None


@dataclass
class Finding:
    analyzer: str
    rule_id: str
    title: str
    description: str
    severity: str | None
    category: str
    affected_elements: list[AffectedElement] = field(default_factory=list)
    wcag_references: list[str] = field(default_factory=list)

    @property
    def impact(self) -> str | None:
        """Legacy report/API spelling for severity."""
        return self.severity

    @property
    def help(self) -> str:
        """Legacy report/API spelling for title."""
        return self.title


@dataclass
class PassedCheck:
    help: str = "Passed check"


@dataclass
class AxeAffectedElementData:
    target: list[str] = field(default_factory=list)
    html: str = ""
    failure_summary: str | None = None


@dataclass
class AxeIssueData:
    impact: str | None
    help: str
    description: str
    rule_id: str
    tags: list[str] = field(default_factory=list)
    affected_elements: list[AxeAffectedElementData] = field(default_factory=list)


@dataclass
class AxeScanData:
    violations: list[AxeIssueData] = field(default_factory=list)
    passes: list[PassedCheck] = field(default_factory=list)


@dataclass
class PageSnapshot:
    requested_url: str
    final_url: str
    title: str
    structure: PageStructure
    viewport: dict[str, int]
    axe_scan: AxeScanData
    visual_text_samples: list[VisualTextSample] = field(default_factory=list)


@dataclass
class AnalyzerResult:
    analyzer: str
    findings: list[Finding] = field(default_factory=list)
    passed_checks: list[PassedCheck] = field(default_factory=list)
    metadata: dict[str, str | int | float] = field(default_factory=dict)
    page_structure: PageStructure | None = None


@dataclass
class ScanMetadata:
    started_at: datetime
    duration_seconds: float
    browser: str
    viewport: dict[str, int]


@dataclass
class SeverityBreakdown:
    critical: int = 0
    serious: int = 0
    moderate: int = 0
    minor: int = 0


@dataclass
class AuditReport:
    url: str
    page: PageStructure
    findings: list[Finding]
    passes: list[PassedCheck]
    severity: SeverityBreakdown
    score: int
    metadata: ScanMetadata

    @property
    def violations(self) -> list[Finding]:
        """Legacy report/API spelling; all current findings are violations."""
        return self.findings
