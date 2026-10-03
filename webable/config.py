"""Configuration values used by the current single-page audit."""

PAGE_TITLE = "WebAble"
PAGE_ICON = "W"
PAGE_LAYOUT = "wide"

VIEWPORT = {"width": 1440, "height": 900}
PAGE_LOAD_WAIT_UNTIL = "domcontentloaded"
PAGE_LOAD_TIMEOUT_MS = 30_000

MAX_SCORE = 100
IMPACT_PENALTIES = {
    "critical": 10,
    "serious": 7,
    "moderate": 4,
    "minor": 2,
}

ANALYSIS_STAGES = {
    "opening": 10,
    "extracting": 30,
    "scanning": 55,
    "reporting": 80,
}
