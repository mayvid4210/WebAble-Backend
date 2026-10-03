"""Existing WebAble page styling."""

STYLES = """
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
"""
