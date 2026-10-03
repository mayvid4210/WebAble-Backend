"""Small, dependency-free utility functions."""

import html


def normalize_url(url: str) -> str:
    """Add HTTPS when a URL has no HTTP(S) scheme, matching the existing UI."""
    if not url.startswith(("http://", "https://")):
        return "https://" + url
    return url


def escape_html_text(value: str) -> str:
    return html.escape(value)
