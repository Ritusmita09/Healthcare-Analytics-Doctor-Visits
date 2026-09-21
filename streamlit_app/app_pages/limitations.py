"""
Data Limitations page — full documentation of dataset limitations.
"""
import streamlit as st

st.title(":material/warning: Data limitations")
st.caption(
    "This page documents known data characteristics, measurement limitations, "
    "and analytical caveats for the Healthcare Doctor Visits dataset."
)

st.divider()

items = [
    (
        ":material/bar_chart: Zero-inflated visit distribution",
        """
**79.8% of respondents report zero doctor visits** in the reference period.

This is an extreme zero inflation that:
- Depresses all group-level means
- Makes medians = 0 for almost every subgroup
- Means standard correlation coefficients may understate true associations among active utilizers
- Renders IQR-based outlier removal inappropriate (IQR = 0 because ≥75% of values = 0)

No zero-visit records were removed. They are treated as genuine survey responses.
        """,
    ),
    (
        ":material/trending_up: Right-skewed visit counts",
        """
Doctor visits range from **0 to 9**, with mean ≈ 0.30 and a high positive skew (≈ 4).

A small number of high-utilizer respondents drive the mean upward.
The mean is not representative of a typical respondent in this dataset.
        """,
    ),
    (
        ":material/person: Self-reported health variables",
        """
The following variables are **self-reported** and not clinically verified:

- `illness` — number of illnesses in the past 2 weeks
- `health` — self-rated health score (0–12)
- `reduced` — days of reduced activity

Self-reporting introduces potential recall bias, social desirability bias, and
inconsistency across respondents. Results involving these variables should be
interpreted with additional caution.
        """,
    ),
    (
        ":material/help: Unknown health-score direction",
        """
The `health` column contains values from **0 to 12**. The scale direction is not documented.

- If higher = worse health: positive correlation with visits is expected (sicker people visit more)
- If higher = better health: positive correlation with visits would be counter-intuitive

**No directional interpretation is made anywhere in this dashboard.**
All health-score charts are labelled neutrally as "health score" without direction.
        """,
    ),
    (
        ":material/calendar_today: reduced = 14 is a measurement ceiling",
        """
The `reduced` variable records days of reduced activity in a **2-week window** (max = 14 days).

**188 respondents (3.6%)** have `reduced = 14`. This means "14 or more days" — not exactly 14.
True values beyond 14 are unknown (censored). These are flagged with `reduced_at_ceiling = 1`
in the processed dataset but are **not treated as outliers or removed**.
        """,
    ),
    (
        ":material/attach_money: income = 0 ambiguity",
        """
**79 respondents (1.5%)** have `income = 0.00`.

Without dataset metadata, it is impossible to confirm whether 0 means:
- Genuinely zero household income
- A missing-value code substituted with 0

No imputation was performed. These respondents are flagged with `income_zero_flag = 1`
and preserved in all analyses.
        """,
    ),
    (
        ":material/wc: Binary gender representation",
        """
The dataset records gender as **two categories only**: 'female' and 'male'.

Non-binary, gender-fluid, and other gender identities are not represented.
Gender-based comparisons in this dashboard are limited to this binary classification.
        """,
    ),
    (
        ":material/public: Unknown dataset provenance",
        """
The dataset file does not contain metadata confirming:

- **Country** of origin
- **Year** of the survey
- **Survey methodology** (sampling method, response rate, weighting)

The data is consistent with the Cameron & Trivedi (1986) Australian health survey dataset,
but this is not confirmed in the file. **No findings are generalized to any specific
country, population, or time period.**
        """,
    ),
    (
        ":material/content_copy: Identical attribute rows",
        """
**1,320 rows (25.4%)** share identical values across all 12 original columns with at least one other row.

This is expected given the limited variable cardinality:
- `age` has only 12 discrete values
- `income` has only 14 discrete values
- Most other variables are binary (yes/no)

These rows represent **distinct survey respondents** who happen to share attribute profiles.
No rows were removed on this basis.
        """,
    ),
    (
        ":material/timeline: Observational, cross-sectional data",
        """
This is a **snapshot survey dataset** — a single observation per respondent.

- No longitudinal tracking is possible
- No before/after comparisons can be made
- Changes over time cannot be observed
- Confounding variables not in the dataset may explain observed associations

All findings represent patterns at a single point in time.
        """,
    ),
    (
        ":material/science: Correlation vs. causation",
        """
**All findings in this project are associational, not causal.**

A Spearman correlation coefficient, a group mean difference, or a statistically significant
Kruskal-Wallis test does not establish that one variable causes a change in another.

Observational survey data cannot establish causation without:
- Randomized controlled design
- Controlling for all confounders
- Temporal ordering of variables
- Replication across independent datasets

> *"Correlation indicates association. It does not establish causation."*
        """,
    ),
]

for icon_title, body in items:
    with st.expander(icon_title, expanded=False):
        st.markdown(body.strip())

st.divider()
st.info(
    ":material/school: This project is an **academic and portfolio EDA project**. "
    "It is not intended for clinical use, policy decisions, or medical advice."
)
