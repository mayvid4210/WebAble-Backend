"""Streamlit application entry point and UI orchestration."""

import time

import streamlit as st

from webable.analysis import run_audit
from webable.config import ANALYSIS_STAGES, PAGE_ICON, PAGE_LAYOUT, PAGE_TITLE
from webable.ui.report_view import render_report
from webable.ui.styles import STYLES


def run_app() -> None:
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=PAGE_LAYOUT,
    )
    st.markdown(STYLES, unsafe_allow_html=True)

    st.markdown(
        '<div class="webable-title">WebAble.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="webable-subtitle">'
        "See your website through every user."
        "</div>",
        unsafe_allow_html=True,
    )

    url = st.text_input(
        "Website URL",
        placeholder="https://yourwebsite.com",
    )
    analyze = st.button("Analyze website", use_container_width=True)

    if not analyze:
        return

    if not url:
        st.info("Enter a website URL to begin.")
        st.stop()

    st.write("")
    loader = st.empty()
    progress = st.progress(0)

    progress_messages = {
        "opening": (
            "### Opening website\n\nConnecting to the page..."
        ),
        "extracting": (
            "### Understanding page structure\n\n"
            "Inspecting links, images, forms and controls..."
        ),
        "scanning": (
            "### Running accessibility checks\n\n"
            "Testing the rendered page against accessibility rules..."
        ),
        "reporting": (
            "### Building your report\n\n"
            "Organizing issues, severity and affected elements..."
        ),
    }

    def update_progress(stage: str) -> None:
        loader.markdown(progress_messages[stage])
        progress.progress(ANALYSIS_STAGES[stage])

    try:
        report = run_audit(url, on_progress=update_progress)
        progress.progress(100)
        loader.markdown(
            "### Report ready\n\n"
            "WebAble has finished analyzing this page."
        )
        time.sleep(0.6)
        progress.empty()
        loader.empty()
        render_report(report)
    except Exception as error:
        progress.empty()
        loader.empty()
        st.info(
            "WebAble couldn't complete this scan. "
            "The website may block automated browsers "
            "or may have taken too long to respond."
        )
        with st.expander("Technical details"):
            st.code(str(error))
