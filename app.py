import streamlit as st
from playwright.sync_api import sync_playwright
from axe_playwright_python.sync_playwright import Axe
import time
import html

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="WebAble",
    page_icon="W",
    layout="wide"
)


# ---------------------------------------------------------
# CSS
# ---------------------------------------------------------

st.markdown("""
<style>

/* ---------- PAGE ---------- */

.stApp {
    background-color: #ffffff;
    color: #111111;
}

.block-container {
    max-width: 1150px;
    padding-top: 4rem;
    padding-bottom: 6rem;
}


/* ---------- HEADER ---------- */

.webable-title {
    font-size: 62px;
    font-weight: 750;
    letter-spacing: -4px;
    line-height: 1;
    color: #111111;
    margin-bottom: 12px;

    animation: fadeUp 0.6s ease;
}

.webable-subtitle {
    font-size: 19px;
    color: #666666;
    margin-bottom: 36px;

    animation: fadeUp 0.8s ease;
}


/* ---------- INPUT ---------- */

.stTextInput label {
    color: #333333 !important;
    font-weight: 500;
}

.stTextInput input {
    background-color: #ffffff !important;
    color: #111111 !important;

    border: 1px solid #d8d8d8 !important;
    border-radius: 12px !important;

    height: 50px;

    transition: all 0.2s ease;
}

.stTextInput input:focus {
    border-color: #111111 !important;
    box-shadow: 0 0 0 1px #111111 !important;
}


/* ---------- BUTTON ---------- */

.stButton > button {

    background-color: #111111 !important;
    color: #ffffff !important;

    border: none !important;
    border-radius: 12px !important;

    height: 50px;

    font-weight: 600;
    font-size: 15px;

    transition:
        transform 0.2s ease,
        opacity 0.2s ease;
}

.stButton > button:hover {

    background-color: #222222 !important;
    color: #ffffff !important;

    transform: translateY(-2px);
}

.stButton > button:active {
    transform: scale(0.99);
}


/* ---------- PROGRESS BAR ---------- */

.stProgress > div > div {
    background-color: #eeeeee !important;
}

.stProgress > div > div > div > div {
    background-color: #111111 !important;
}


/* ---------- REPORT ---------- */

.report-label {

    font-size: 12px;
    font-weight: 700;

    letter-spacing: 2px;

    color: #888888;

    margin-bottom: 8px;
}

.website-title {

    font-size: 38px;
    font-weight: 700;

    letter-spacing: -1.5px;

    color: #111111;

    animation: fadeUp 0.5s ease;
}


/* ---------- SCORE ---------- */

.score-number {

    font-size: 76px;
    font-weight: 750;

    letter-spacing: -5px;
    line-height: 1;

    color: #111111;

    animation: scoreAppear 0.7s ease;
}

.score-label {

    margin-top: 12px;

    color: #707070;

    font-size: 13px;
    font-weight: 500;

    letter-spacing: 0.4px;
}


/* ---------- METRIC CARDS ---------- */

[data-testid="stMetric"] {

    background-color: #f7f7f7 !important;

    border: 1px solid #e2e2e2 !important;

    padding: 22px !important;

    border-radius: 16px !important;

    min-height: 120px;

    transition:
        transform 0.2s ease,
        border-color 0.2s ease,
        box-shadow 0.2s ease;

    animation: fadeUp 0.5s ease;
}

[data-testid="stMetric"]:hover {

    transform: translateY(-4px);

    border-color: #aaaaaa !important;

    box-shadow:
        0 8px 25px rgba(0, 0, 0, 0.05);
}


/* METRIC LABEL */

[data-testid="stMetricLabel"] {

    color: #666666 !important;

    font-size: 14px !important;
}

[data-testid="stMetricLabel"] * {

    color: #666666 !important;
}


/* METRIC NUMBER */

[data-testid="stMetricValue"] {

    color: #111111 !important;

    font-size: 32px !important;

    font-weight: 650 !important;
}

[data-testid="stMetricValue"] * {

    color: #111111 !important;
}


/* ---------- EXPANDERS ---------- */

[data-testid="stExpander"] {

    background-color: #fafafa !important;

    border: 1px solid #e3e3e3 !important;

    border-radius: 14px !important;

    margin-bottom: 10px;

    overflow: hidden;

    transition:
        transform 0.2s ease,
        border-color 0.2s ease;
}

[data-testid="stExpander"]:hover {

    transform: translateY(-2px);

    border-color: #aaaaaa !important;
}

[data-testid="stExpander"] summary {

    color: #111111 !important;

    font-weight: 550;
}

[data-testid="stExpander"] summary * {

    color: #111111 !important;
}


/* ---------- ALERTS ---------- */

[data-testid="stAlert"] {

    background-color: #f6f6f6 !important;

    border: 1px solid #dddddd !important;

    color: #111111 !important;

    border-radius: 14px !important;
}

[data-testid="stAlert"] * {

    color: #111111 !important;
}


/* ---------- CODE ---------- */

.stCodeBlock {

    border-radius: 12px;

    border: 1px solid #e2e2e2;
}


/* ---------- DIVIDERS ---------- */

hr {

    border-color: #eeeeee !important;

    margin-top: 45px !important;
    margin-bottom: 45px !important;
}


/* ---------- HEADINGS ---------- */

h1, h2, h3 {

    color: #111111 !important;

    letter-spacing: -1px;
}


/* ---------- LINKS ---------- */

a {

    color: #444444 !important;

    text-decoration-color: #aaaaaa !important;
}


/* ---------- ANIMATIONS ---------- */

@keyframes fadeUp {

    from {
        opacity: 0;
        transform: translateY(14px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}


@keyframes scoreAppear {

    from {
        opacity: 0;
        transform: scale(0.92);
    }

    to {
        opacity: 1;
        transform: scale(1);
    }
}


/* ---------- HIDE STREAMLIT DECORATION ---------- */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.markdown(
    '<div class="webable-title">WebAble.</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="webable-subtitle">'
    'See your website through every user.'
    '</div>',
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# URL INPUT
# ---------------------------------------------------------

url = st.text_input(
    "Website URL",
    placeholder="https://yourwebsite.com"
)

analyze = st.button(
    "Analyze website",
    use_container_width=True
)


# ---------------------------------------------------------
# ANALYSIS
# ---------------------------------------------------------

if analyze:

    if not url:

        st.info("Enter a website URL to begin.")

        st.stop()


    if not url.startswith(("http://", "https://")):

        url = "https://" + url


    st.write("")

    loader = st.empty()

    progress = st.progress(0)


    try:

        # -------------------------------------------------
        # STAGE 1
        # -------------------------------------------------

        loader.markdown(
            """
            ### Opening website

            Connecting to the page...
            """
        )

        progress.progress(10)


        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=True
            )

            page = browser.new_page(

                viewport={
                    "width": 1440,
                    "height": 900
                }
            )


            page.goto(

                url,

                wait_until="domcontentloaded",

                timeout=30000
            )


            # -------------------------------------------------
            # STAGE 2
            # -------------------------------------------------

            progress.progress(30)

            loader.markdown(
                """
                ### Understanding page structure

                Inspecting links, images, forms and controls...
                """
            )


            title = page.title()


            links = page.locator(
                "a"
            ).count()


            images = page.locator(
                "img"
            ).count()


            buttons = page.locator(
                "button"
            ).count()


            forms = page.locator(
                "form"
            ).count()


            inputs = page.locator(
                "input"
            ).count()


            headings = page.locator(
                "h1, h2, h3, h4, h5, h6"
            ).count()


            images_without_alt = page.locator(
                "img:not([alt])"
            ).count()


            # -------------------------------------------------
            # STAGE 3
            # -------------------------------------------------

            progress.progress(55)

            loader.markdown(
                """
                ### Running accessibility checks

                Testing the rendered page against accessibility rules...
                """
            )


            axe = Axe()

            results = axe.run(
                page
            )


            violations = results.response[
                "violations"
            ]


            passes = results.response[
                "passes"
            ]


            # -------------------------------------------------
            # STAGE 4
            # -------------------------------------------------

            progress.progress(80)

            loader.markdown(
                """
                ### Building your report

                Organizing issues, severity and affected elements...
                """
            )


            browser.close()


        # ---------------------------------------------------------
        # CALCULATE SEVERITY
        # ---------------------------------------------------------

        critical = 0

        serious = 0

        moderate = 0

        minor = 0


        penalty = 0


        for issue in violations:

            impact = issue.get(
                "impact"
            )


            if impact == "critical":

                critical += 1

                penalty += 10


            elif impact == "serious":

                serious += 1

                penalty += 7


            elif impact == "moderate":

                moderate += 1

                penalty += 4


            elif impact == "minor":

                minor += 1

                penalty += 2


        score = max(
            0,
            100 - penalty
        )


        # ---------------------------------------------------------
        # FINISH LOADER
        # ---------------------------------------------------------

        progress.progress(100)


        loader.markdown(
            """
            ### Report ready

            WebAble has finished analyzing this page.
            """
        )


        time.sleep(0.6)


        progress.empty()

        loader.empty()


        # ---------------------------------------------------------
        # REPORT HEADER
        # ---------------------------------------------------------

        safe_title = html.escape(
            title
        )


        st.markdown(
            '<div class="report-label">'
            'WEBABLE AUDIT'
            '</div>',
            unsafe_allow_html=True
        )


        st.markdown(

            f'<div class="website-title">'
            f'{safe_title}'
            f'</div>',

            unsafe_allow_html=True
        )


        st.caption(
            url
        )


        st.write("")

        st.write("")


        # ---------------------------------------------------------
        # SCORE
        # ---------------------------------------------------------

        score_column, explanation_column = st.columns(
            [1, 2]
        )


        with score_column:

            st.markdown(

                f'<div class="score-number">'
                f'{score}'
                f'</div>',

                unsafe_allow_html=True
            )


            st.markdown(

                '<div class="score-label">'
                'AUTOMATED ACCESSIBILITY SCORE / 100'
                '</div>',

                unsafe_allow_html=True
            )


        with explanation_column:

            st.write("")

            st.write("")


            st.progress(
                score
            )


            if score >= 90:

                st.markdown(
                    """
                    **Strong automated result**

                    Few detectable barriers were found on this page.
                    """
                )


            elif score >= 70:

                st.markdown(
                    """
                    **Good foundation**

                    Some detectable accessibility barriers need attention.
                    """
                )


            else:

                st.markdown(
                    """
                    **Accessibility improvements recommended**

                    Multiple detectable barriers were found on this page.
                    """
                )


        # ---------------------------------------------------------
        # AT A GLANCE
        # ---------------------------------------------------------

        st.divider()


        st.subheader(
            "At a glance"
        )


        col1, col2, col3, col4 = st.columns(
            4
        )


        col1.metric(
            "Issues found",
            len(violations)
        )


        col2.metric(
            "Checks passed",
            len(passes)
        )


        col3.metric(
            "Missing alt text",
            images_without_alt
        )


        elements_scanned = (
            links
            + images
            + buttons
            + inputs
        )


        col4.metric(
            "Elements scanned",
            elements_scanned
        )


        # ---------------------------------------------------------
        # ISSUE BREAKDOWN
        # ---------------------------------------------------------

        st.write("")

        st.subheader(
            "Issue breakdown"
        )


        col1, col2, col3, col4 = st.columns(
            4
        )


        col1.metric(
            "Critical",
            critical
        )


        col2.metric(
            "Serious",
            serious
        )


        col3.metric(
            "Moderate",
            moderate
        )


        col4.metric(
            "Minor",
            minor
        )


        # ---------------------------------------------------------
        # PAGE STRUCTURE
        # ---------------------------------------------------------

        st.divider()


        st.subheader(
            "Page structure"
        )


        col1, col2, col3 = st.columns(
            3
        )


        col1.metric(
            "Links",
            links
        )


        col1.metric(
            "Buttons",
            buttons
        )


        col2.metric(
            "Images",
            images
        )


        col2.metric(
            "Forms",
            forms
        )


        col3.metric(
            "Inputs",
            inputs
        )


        col3.metric(
            "Headings",
            headings
        )


        # ---------------------------------------------------------
        # ACCESSIBILITY ISSUES
        # ---------------------------------------------------------

        st.divider()


        st.subheader(
            "What WebAble noticed"
        )


        if len(violations) == 0:

            st.info(
                "No violations were detected "
                "by the automated accessibility audit."
            )


        else:

            for issue in violations:

                impact = (
                    issue.get("impact")
                    or "unknown"
                )


                issue_help = issue.get(
                    "help",
                    "Accessibility issue"
                )


                with st.expander(

                    f"{impact.upper()}  ·  {issue_help}"
                ):

                    st.markdown(
                        "**What we found**"
                    )


                    st.write(
                        issue.get(
                            "description",
                            ""
                        )
                    )


                    nodes = issue.get(
                        "nodes",
                        []
                    )


                    st.markdown(
                        "**Elements affected**"
                    )


                    st.write(
                        len(nodes)
                    )


                    st.markdown(
                        "**Accessibility rule**"
                    )


                    st.code(
                        issue.get(
                            "id",
                            ""
                        )
                    )


                    # ---------------------------------------------
                    # WCAG REFERENCES
                    # ---------------------------------------------

                    wcag_tags = [

                        tag

                        for tag in issue.get(
                            "tags",
                            []
                        )

                        if tag.startswith(
                            "wcag"
                        )
                    ]


                    if wcag_tags:

                        st.markdown(
                            "**WCAG references**"
                        )


                        st.write(
                            ", ".join(
                                wcag_tags
                            )
                        )


                    # ---------------------------------------------
                    # AFFECTED HTML
                    # ---------------------------------------------

                    if nodes:

                        st.markdown(
                            "**Example affected element**"
                        )


                        affected_html = nodes[0].get(
                            "html",
                            ""
                        )


                        st.code(
                            affected_html,
                            language="html"
                        )


                        failure_summary = nodes[0].get(
                            "failureSummary"
                        )


                        if failure_summary:

                            st.markdown(
                                "**Why this failed**"
                            )


                            st.write(
                                failure_summary
                            )


        # ---------------------------------------------------------
        # PASSED CHECKS
        # ---------------------------------------------------------

        st.divider()


        st.subheader(
            "What already works"
        )


        st.markdown(

            f"**{len(passes)} automated "
            f"accessibility checks passed.**"
        )


        with st.expander(
            "Explore passed checks"
        ):

            for check in passes:

                st.write(
                    "✓ "
                    + check.get(
                        "help",
                        "Passed check"
                    )
                )


        # ---------------------------------------------------------
        # DISCLAIMER
        # ---------------------------------------------------------

        st.divider()


        st.caption(
            "This is an automated page-level accessibility audit. "
            "A high automated score does not guarantee full WCAG "
            "conformance or complete accessibility."
        )


    # ---------------------------------------------------------
    # ERROR
    # ---------------------------------------------------------

    except Exception as e:

        progress.empty()

        loader.empty()


        st.info(
            "WebAble couldn't complete this scan. "
            "The website may block automated browsers "
            "or may have taken too long to respond."
        )


        with st.expander(
            "Technical details"
        ):

            st.code(
                str(e)
            )