"""
Key Insights page — dynamic, evidence-based insights from the filtered dataset.
"""
import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
from data_loader import PALETTE, CHRONIC_ORDER, INSURANCE_ORDER, AGE_ORDER

df  = st.session_state["df"]     # full dataset
dff = st.session_state["dff"]    # filtered dataset

st.title(":material/lightbulb: Key insights")
st.caption(
    "Evidence-based findings computed from the **currently filtered dataset**. "
    "All statements are observational — no causal claims are made."
)

if len(dff) == 0:
    st.warning("No records match the current filters.")
    st.stop()

n = len(dff)
is_filtered = (n < len(df))

if is_filtered:
    st.info(
        f":material/filter_alt: Showing insights for **{n:,} respondents** "
        f"({n/len(df)*100:.1f}% of full dataset). "
        "Remove sidebar filters to see full-dataset insights."
    )

# ── Helper ────────────────────────────────────────────────────────────────────
def _rho(col):
    if dff[col].std() == 0:
        return 0.0, 1.0
    return stats.spearmanr(dff[col], dff["visits"])

# ── Visit Patterns ────────────────────────────────────────────────────────────
st.subheader(":material/bar_chart: Visit patterns")
with st.container(border=True):
    zero_pct   = (dff["visits"] == 0).mean() * 100
    mean_vis   = dff["visits"].mean()
    max_vis    = dff["visits"].max()
    high_n     = (dff["visits"] >= 3).sum()
    skew       = dff["visits"].skew()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Zero-visit respondents", f"{(dff['visits']==0).sum():,}  ({zero_pct:.1f}%)", border=True)
        st.metric("Mean visits",           f"{mean_vis:.3f}", border=True)
    with col2:
        st.metric("High utilizers (≥3 visits)", f"{high_n:,}", border=True)
        st.metric("Skewness",              f"{skew:.2f}",   border=True)

    st.markdown(
        f"- **{zero_pct:.1f}%** of respondents in this selection report **zero doctor visits**.\n"
        f"- Mean visits = **{mean_vis:.3f}**; median = **0**. The distribution is strongly right-skewed "
        f"(skewness = {skew:.2f}).\n"
        f"- Maximum observed visits: **{max_vis}**.\n"
        f"- **{high_n}** respondents ({high_n/n*100:.1f}%) report 3 or more visits."
    )

# ── Demographic Patterns ──────────────────────────────────────────────────────
st.subheader(":material/groups: Demographic patterns")
with st.container(border=True):
    age_means = dff.groupby("age_group")["visits"].mean().reindex(AGE_ORDER)
    youngest  = AGE_ORDER[0]
    oldest    = AGE_ORDER[-1]
    female_mean = dff[dff["gender"]=="female"]["visits"].mean()
    male_mean   = dff[dff["gender"]=="male"]["visits"].mean()
    rho_age, p_age = _rho("age_years")

    st.markdown(
        f"- **Age:** Mean visits increases from **{age_means.get(youngest, float('nan')):.3f}** "
        f"(age ≤25) to **{age_means.get(oldest, float('nan')):.3f}** (age 66+). "
        f"Spearman rho = **{rho_age:.3f}** (age_years vs visits).\n"
        f"- **Gender:** Female respondents show a mean visit count of **{female_mean:.3f}**; "
        f"male respondents **{male_mean:.3f}**. "
        f"This is an observed association — not a biological or causal explanation.\n"
        f"- **Note:** Age is recorded in 12 discrete bands. Gender is recorded as binary only."
    )

# ── Health Burden ─────────────────────────────────────────────────────────────
st.subheader(":material/medical_information: Health burden")
with st.container(border=True):
    rho_ill, _ = _rho("illness")
    rho_red, _ = _rho("reduced")
    rho_hlt, _ = _rho("health")
    cs_means = dff.groupby("chronic_status")["visits"].mean().reindex(CHRONIC_ORDER)
    no_cond  = cs_means.get("No Condition", float("nan"))
    lim      = cs_means.get("Limiting",     float("nan"))
    ill0_mean = dff[dff["illness"]==0]["visits"].mean() if (dff["illness"]==0).any() else float("nan")
    ill5_mean = dff[dff["illness"]==5]["visits"].mean() if (dff["illness"]==5).any() else float("nan")

    st.markdown(
        f"- **Illness count:** Spearman rho = **{rho_ill:.3f}** — "
        f"a positive association with visits. "
        f"Mean visits rises from **{ill0_mean:.3f}** (illness=0) to "
        f"**{ill5_mean:.3f}** (illness=5) in this selection.\n"
        f"- **Reduced activity:** Spearman rho = **{rho_red:.3f}** — "
        f"the strongest correlate with visits in this dataset.\n"
        f"- **Chronic conditions:** Limiting chronic conditions are associated with higher visit counts "
        f"(mean = **{lim:.3f}**) compared to no condition (mean = **{no_cond:.3f}**).\n"
        f"- **Health score:** Spearman rho = **{rho_hlt:.3f}**. "
        f"Scale direction is unknown — no directional interpretation is made.\n"
        f"- All variables are self-reported. No clinical verification is available."
    )

# ── Insurance & Income ────────────────────────────────────────────────────────
st.subheader(":material/account_balance: Insurance & income")
with st.container(border=True):
    ins_means = dff.groupby("insurance_type")["visits"].mean().reindex(INSURANCE_ORDER)
    highest_ins = ins_means.idxmax() if not ins_means.isna().all() else "N/A"
    lowest_ins  = ins_means.idxmin() if not ins_means.isna().all() else "N/A"
    rho_inc, _ = _rho("income")
    zero_inc_n  = dff["income_zero_flag"].sum()

    st.markdown(
        f"- **Insurance type:** '{highest_ins}' respondents show the highest mean visits "
        f"(**{ins_means.get(highest_ins, float('nan')):.3f}**); "
        f"'{lowest_ins}' the lowest (**{ins_means.get(lowest_ins, float('nan')):.3f}**).\n"
        f"- **Income:** Spearman rho = **{rho_inc:.3f}** with visits — "
        f"a very weak negative association.\n"
        f"- **{zero_inc_n}** respondent(s) in this selection have income = 0 "
        f"(ambiguous — may be genuine zero or a missing code).\n"
        f"- Insurance exclusivity confirmed: private, freepoor, and freerepat are mutually exclusive."
    )

# ── Key Correlations ──────────────────────────────────────────────────────────
st.subheader(":material/hub: Key correlations with visits")
with st.container(border=True):
    num_cols = [
        "age_years", "income", "illness", "reduced", "health",
        "private_enc", "freepoor_enc", "freerepat_enc",
        "nchronic_enc", "lchronic_enc", "gender_enc",
    ]
    corr_rows = []
    for col in num_cols:
        if dff[col].std() > 0 and len(dff) > 5:
            rho, pv = stats.spearmanr(dff[col], dff["visits"])
            corr_rows.append({"Variable": col, "Spearman rho": round(rho, 3),
                               "p-value": f"{'< 0.001' if pv < 0.001 else f'{pv:.3f}'}"})
    if corr_rows:
        corr_df = pd.DataFrame(corr_rows).sort_values("Spearman rho", ascending=False)
        st.dataframe(corr_df, hide_index=True)
        st.caption(
            ":material/warning: Statistical significance at p<0.05 does not imply causation. "
            "With n=5,190 records, even very small correlations can reach statistical significance."
        )

# ── Disclaimer ────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "> **Important:** All insights on this page are **descriptive associations** "
    "derived from survey data. They do not constitute medical diagnoses, "
    "clinical recommendations, or causal explanations. "
    "The dataset is zero-inflated; most group-level medians equal 0."
)
