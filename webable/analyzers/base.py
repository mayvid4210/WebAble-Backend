"""Shared contract for page analyzers."""

from typing import Protocol, runtime_checkable

from webable.models import AnalyzerResult, PageSnapshot


@runtime_checkable
class Analyzer(Protocol):
    @property
    def name(self) -> str: ...

    def analyze(self, snapshot: PageSnapshot) -> AnalyzerResult: ...
