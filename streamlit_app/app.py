"""
app.py — Healthcare Analytics for Doctor Visits
Main Streamlit entry point.

Run from the project root:
    python -m streamlit run streamlit_app/app.py
"""
import sys
import pathlib

# Ensure the streamlit_app directory is on sys.path so page modules
# can import data_loader without a relative-import error.
_HERE = pathlib.Path(__file__).parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import streamlit as st
from data_loader import load_data, sidebar_filters, apply_filters

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Healthcare Analytics — Doctor Visits",
    page_icon=":material/local_hospital:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": (
            "**Healthcare Analytics for Doctor Visits**\n\n"
            "Portfolio project — exploratory data analysis of a healthcare survey dataset.\n"
            "All findings are observational. No causal claims are made."
        )
    },
)

# ── Load data once ────────────────────────────────────────────────────────────
df = load_data()

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### :material/monitor_heart: Healthcare Analytics")
    st.caption("Doctor Visits Dataset · 5,190 respondents")
    st.divider()

filters = sidebar_filters(df)
dff = apply_filters(df, filters)

# Store in session_state so page modules can access without re-filtering
st.session_state["df"]      = df
st.session_state["dff"]     = dff
st.session_state["filters"] = filters

# ── Navigation ────────────────────────────────────────────────────────────────
page = st.navigation(
    {
        "Dashboard": [
            st.Page("app_pages/overview.py",         title="Overview",          icon=":material/dashboard:"),
            st.Page("app_pages/visit_patterns.py",   title="Visit patterns",    icon=":material/bar_chart:"),
        ],
        "Analysis": [
            st.Page("app_pages/demographics.py",     title="Demographics",      icon=":material/groups:"),
            st.Page("app_pages/health_burden.py",    title="Health burden",     icon=":material/medical_information:"),
            st.Page("app_pages/insurance_income.py", title="Insurance & income", icon=":material/account_balance:"),
            st.Page("app_pages/relationships.py",    title="Relationships",     icon=":material/hub:"),
        ],
        "Summary": [
            st.Page("app_pages/key_insights.py",     title="Key insights",      icon=":material/lightbulb:"),
            st.Page("app_pages/limitations.py",      title="Data limitations",  icon=":material/warning:"),
        ],
    },
    position="sidebar",
)

page.run()
