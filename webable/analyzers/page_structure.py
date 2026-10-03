"""Analyzer that exposes the existing extracted page structure metrics."""

from webable.models import AnalyzerResult, PageSnapshot


class PageStructureAnalyzer:
    name = "page_structure"

    def analyze(self, snapshot: PageSnapshot) -> AnalyzerResult:
        return AnalyzerResult(
            analyzer=self.name,
            page_structure=snapshot.structure,
        )
