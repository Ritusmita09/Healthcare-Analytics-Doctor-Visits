"""
data_loader.py
Shared, cached data-loading module for the Healthcare Analytics dashboard.
Run from the project root: python -m streamlit run streamlit_app/app.py
"""
import pathlib
import pandas as pd
import streamlit as st

# Resolve the processed CSV relative to the project root (two levels up from this file)
_HERE = pathlib.Path(__file__).parent          # streamlit_app/
_ROOT = _HERE.parent                            # project root
_PROC = _ROOT / "data" / "processed" / "doctor_visits_clean.csv"

REQUIRED_COLUMNS = [
    "visits", "gender", "age", "income", "illness", "reduced", "health",
    "private", "freepoor", "freerepat", "nchronic", "lchronic",
    "age_years", "age_group", "income_zero_flag", "income_group",
    "private_enc", "freepoor_enc", "freerepat_enc",
    "nchronic_enc", "lchronic_enc", "gender_enc",
    "insurance_type", "chronic_status", "visit_group", "reduced_at_ceiling",
]

# Ordered category definitions shared across all pages
AGE_ORDER      = ["<=25", "26-35", "36-45", "46-55", "56-65", "66+"]
INCOME_ORDER   = ["Low(0-0.15)", "Lower-Mid(0.16-0.45)", "Upper-Mid(0.46-0.75)", "High(0.76-1.50)"]
CHRONIC_ORDER  = ["No Condition", "Non-Limiting", "Limiting"]
INSURANCE_ORDER = ["Private", "Free-Poor", "Free-Repatriated", "Uninsured"]
VISIT_GRP_ORDER = ["0 visits", "1-2 visits", "3-5 visits", "6+ visits"]

# Plotly colour palette (consistent across charts)
PALETTE = {
    "primary":   "#2563EB",
    "secondary": "#059669",
    "accent":    "#D97706",
    "danger":    "#DC2626",
    "muted":     "#64748B",
    "light":     "#E0E7FF",
}

CHART_COLORS = ["#2563EB", "#059669", "#D97706", "#DC2626", "#7C3AED", "#0891B2", "#BE185D"]


@st.cache_data(ttl=3600, show_spinner="Loading dataset…")
def load_data() -> pd.DataFrame:
    """Load and validate the processed dataset. Cached for the session."""
    if not _PROC.exists():
        st.error(
            f"Processed dataset not found at `{_PROC}`.  \n"
            "Run the cleaning script first: `python streamlit_app/data_loader.py`"
        )
        st.stop()

    df = pd.read_csv(_PROC)

    # Validate required columns
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        st.error(f"Missing columns in processed dataset: {missing}")
        st.stop()

    # Validate no missing values in key columns
    null_counts = df[REQUIRED_COLUMNS].isnull().sum()
    if null_counts.sum() > 0:
        st.warning(f"Unexpected nulls detected:\n{null_counts[null_counts > 0].to_string()}")

    return df


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Apply sidebar filter selections to the dataframe."""
    dff = df.copy()

    # Gender
    if filters.get("gender") and "All" not in filters["gender"]:
        dff = dff[dff["gender"].isin(filters["gender"])]

    # Age group
    if filters.get("age_group") and "All" not in filters["age_group"]:
        dff = dff[dff["age_group"].isin(filters["age_group"])]

    # Insurance type
    if filters.get("insurance_type") and "All" not in filters["insurance_type"]:
        dff = dff[dff["insurance_type"].isin(filters["insurance_type"])]

    # Chronic status
    if filters.get("chronic_status") and "All" not in filters["chronic_status"]:
        dff = dff[dff["chronic_status"].isin(filters["chronic_status"])]

    # Visit group
    if filters.get("visit_group") and "All" not in filters["visit_group"]:
        dff = dff[dff["visit_group"].isin(filters["visit_group"])]

    # Illness range
    if filters.get("illness_range"):
        lo, hi = filters["illness_range"]
        dff = dff[(dff["illness"] >= lo) & (dff["illness"] <= hi)]

    return dff


def sidebar_filters(df: pd.DataFrame) -> dict:
    """Render sidebar filters and return the selection dict."""
    with st.sidebar:
        st.markdown("## :material/filter_alt: Filters")
        st.caption(f"Full dataset: {len(df):,} respondents")
        st.divider()

        gender = st.multiselect(
            "Gender",
            options=["All"] + sorted(df["gender"].unique().tolist()),
            default=["All"],
            key="filter_gender",
        )

        age_group = st.multiselect(
            "Age group",
            options=["All"] + AGE_ORDER,
            default=["All"],
            key="filter_age_group",
        )

        insurance_type = st.multiselect(
            "Insurance type",
            options=["All"] + INSURANCE_ORDER,
            default=["All"],
            key="filter_insurance",
        )

        chronic_status = st.multiselect(
            "Chronic condition status",
            options=["All"] + CHRONIC_ORDER,
            default=["All"],
            key="filter_chronic",
        )

        visit_group = st.multiselect(
            "Visit group",
            options=["All"] + VISIT_GRP_ORDER,
            default=["All"],
            key="filter_visit_group",
        )

        illness_range = st.slider(
            "Illness count (0–5)",
            min_value=0, max_value=5,
            value=(0, 5),
            key="filter_illness",
        )

        st.divider()
        if st.button(":material/restart_alt: Reset all filters", key="reset_filters"):
            for k in ["filter_gender", "filter_age_group", "filter_insurance",
                      "filter_chronic", "filter_visit_group", "filter_illness"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

        filters = {
            "gender": gender,
            "age_group": age_group,
            "insurance_type": insurance_type,
            "chronic_status": chronic_status,
            "visit_group": visit_group,
            "illness_range": illness_range,
        }

        dff = apply_filters(df, filters)
        n = len(dff)
        pct = n / len(df) * 100
        if n == len(df):
            st.success(f":material/check_circle: All {n:,} respondents")
        elif n == 0:
            st.error(":material/warning: No respondents match the selected filters.")
        else:
            st.info(f":material/filter_alt: {n:,} respondents ({pct:.1f}%)")

    return filters
