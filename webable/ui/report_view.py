"""Streamlit rendering for a completed audit report."""

import streamlit as st

from webable.models import AuditReport
from webable.utils import escape_html_text


def render_report(report: AuditReport) -> None:
    page = report.page

    st.markdown(
        '<div class="report-label">WEBABLE AUDIT</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="website-title">{escape_html_text(page.title)}</div>',
        unsafe_allow_html=True,
    )
    st.caption(report.url)
    st.write("")
    st.write("")

    _render_score(report)
    st.divider()
    _render_overview(report)
    st.write("")
    _render_severity(report)
    st.divider()
    _render_page_structure(report)
    st.divider()
    _render_violations(report)
    st.divider()
    _render_passes(report)
    st.divider()
    st.caption(
        "This is an automated page-level accessibility audit. "
        "A high automated score does not guarantee full WCAG "
        "conformance or complete accessibility."
    )


def _render_score(report: AuditReport) -> None:
    score_column, explanation_column = st.columns([1, 2])

    with score_column:
        st.markdown(
            f'<div class="score-number">{report.score}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="score-label">'
            "AUTOMATED ACCESSIBILITY SCORE / 100"
            "</div>",
            unsafe_allow_html=True,
        )

    with explanation_column:
        st.write("")
        st.write("")
        st.progress(report.score)

        if report.score >= 90:
            st.markdown(
                "**Strong automated result**\n\n"
                "Few detectable barriers were found on this page."
            )
        elif report.score >= 70:
            st.markdown(
                "**Good foundation**\n\n"
                "Some detectable accessibility barriers need attention."
            )
        else:
            st.markdown(
                "**Accessibility improvements recommended**\n\n"
                "Multiple detectable barriers were found on this page."
            )


def _render_overview(report: AuditReport) -> None:
    st.subheader("At a glance")
    columns = st.columns(4)
    columns[0].metric("Issues found", len(report.violations))
    columns[1].metric("Checks passed", len(report.passes))
    columns[2].metric("Missing alt text", report.page.images_without_alt)
    columns[3].metric("Elements scanned", report.page.elements_scanned)


def _render_severity(report: AuditReport) -> None:
    st.subheader("Issue breakdown")
    columns = st.columns(4)
    columns[0].metric("Critical", report.severity.critical)
    columns[1].metric("Serious", report.severity.serious)
    columns[2].metric("Moderate", report.severity.moderate)
    columns[3].metric("Minor", report.severity.minor)


def _render_page_structure(report: AuditReport) -> None:
    st.subheader("Page structure")
    columns = st.columns(3)
    columns[0].metric("Links", report.page.links)
    columns[0].metric("Buttons", report.page.buttons)
    columns[1].metric("Images", report.page.images)
    columns[1].metric("Forms", report.page.forms)
    columns[2].metric("Inputs", report.page.inputs)
    columns[2].metric("Headings", report.page.headings)


def _render_violations(report: AuditReport) -> None:
    st.subheader("What WebAble noticed")

    if not report.violations:
        st.info(
            "No violations were detected "
            "by the automated accessibility audit."
        )
        return

    for issue in report.violations:
        impact = issue.impact or "unknown"
        with st.expander(f"{impact.upper()}  ·  {issue.help}"):
            st.markdown("**What we found**")
            st.write(issue.description)

            st.markdown("**Elements affected**")
            st.write(len(issue.affected_elements))

            st.markdown("**Accessibility rule**")
            st.code(issue.rule_id)

            if issue.wcag_references:
                st.markdown("**WCAG references**")
                st.write(", ".join(issue.wcag_references))

            if issue.affected_elements:
                node = issue.affected_elements[0]
                st.markdown("**Example affected element**")
                st.code(node.html, language="html")

                if node.failure_summary:
                    st.markdown("**Why this failed**")
                    st.write(node.failure_summary)


def _render_passes(report: AuditReport) -> None:
    st.subheader("What already works")
    st.markdown(
        f"**{len(report.passes)} automated "
        "accessibility checks passed.**"
    )

    with st.expander("Explore passed checks"):
        for check in report.passes:
            st.write("✓ " + check.help)
