"""
Relationships page — Spearman correlations and scatter charts.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy import stats
from data_loader import PALETTE, CHART_COLORS

dff = st.session_state["dff"]

st.title(":material/hub: Relationships")
st.caption(
    "Spearman rank correlations and bivariate associations between key variables. "
    "**All correlations indicate association only — they do not establish causation.**"
)

if len(dff) == 0:
    st.warning("No records match the current filters.")
    st.stop()

if len(dff) < 10:
    st.warning("Fewer than 10 respondents selected — correlation results may not be meaningful.")

# ── Correlation matrix ────────────────────────────────────────────────────────
st.subheader("Spearman correlation matrix")

num_cols = [
    "visits", "age_years", "income", "illness", "reduced", "health",
    "private_enc", "freepoor_enc", "freerepat_enc",
    "nchronic_enc", "lchronic_enc", "gender_enc",
]
col_labels = {
    "visits": "Visits",
    "age_years": "Age (years)",
    "income": "Income",
    "illness": "Illness count",
    "reduced": "Reduced days",
    "health": "Health score",
    "private_enc": "Private insur.",
    "freepoor_enc": "Free-Poor insur.",
    "freerepat_enc": "Free-Repat. insur.",
    "nchronic_enc": "Non-lim. chronic",
    "lchronic_enc": "Lim. chronic",
    "gender_enc": "Gender (M=1)",
}

corr = dff[num_cols].corr(method="spearman").round(3)
corr_display = corr.rename(index=col_labels, columns=col_labels)

fig_heatmap = px.imshow(
    corr_display,
    color_continuous_scale="RdBu_r",
    zmin=-1, zmax=1,
    aspect="auto",
    text_auto=".2f",
    labels=dict(color="Spearman rho"),
)
fig_heatmap.update_layout(
    margin=dict(l=5, r=5, t=5, b=5),
    coloraxis_colorbar_title="rho",
)
st.plotly_chart(fig_heatmap, key="rel_heatmap")

st.caption(
    "Colour: red = positive association, blue = negative association, white = near zero. "
    "All values are Spearman rank correlations calculated from the filtered dataset."
)

st.info(
    ":material/warning: **Correlation ≠ Causation.** "
    "A non-zero correlation means two variables move together monotonically. "
    "It does not mean one variable causes the other.",
)

st.divider()

# ── Correlations with visits ──────────────────────────────────────────────────
st.subheader("Correlations with visits (sorted)")

visit_corr = corr["visits"].drop("visits").sort_values(ascending=False).reset_index()
visit_corr.columns = ["variable", "rho"]
visit_corr["label"] = visit_corr["variable"].map(col_labels).fillna(visit_corr["variable"])
visit_corr["direction"] = visit_corr["rho"].apply(
    lambda r: "Positive" if r > 0 else ("Negative" if r < 0 else "None")
)

fig_bar = px.bar(
    visit_corr, x="rho", y="label",
    orientation="h",
    color="direction",
    color_discrete_map={"Positive": PALETTE["primary"], "Negative": PALETTE["danger"], "None": PALETTE["muted"]},
    labels={"rho": "Spearman rho with visits", "label": "Variable"},
    text=visit_corr["rho"].round(3),
)
fig_bar.add_vline(x=0, line_dash="solid", line_color="#94A3B8")
fig_bar.update_traces(textposition="outside")
fig_bar.update_layout(
    plot_bgcolor="white",
    xaxis_gridcolor="#E5E7EB",
    showlegend=False,
    margin=dict(l=5, r=5, t=5, b=5),
    yaxis={"categoryorder": "total ascending"},
)
st.plotly_chart(fig_bar, key="rel_corr_bar")

st.divider()

# ── Bivariate scatter charts ──────────────────────────────────────────────────
st.subheader("Key bivariate associations")

rng = np.random.RandomState(77)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Reduced vs visits",
    "Illness vs visits",
    "Age vs visits",
    "Income vs visits",
    "Health score vs visits",
])

def _scatter_tab(x_col, x_label, y_col="visits", rho_hint=None, notes=None, jitter_x=0.25, jitter_y=0.15, key=""):
    j_x = rng.uniform(-jitter_x, jitter_x, len(dff))
    j_y = rng.uniform(-jitter_y, jitter_y, len(dff))
    rho, pval = stats.spearmanr(dff[x_col], dff[y_col])
    title_str = f"Spearman rho = {rho:.3f}  (p {'< 0.001' if pval < 0.001 else f'= {pval:.3f}'})"
    fig = px.scatter(
        x=dff[x_col] + j_x,
        y=dff[y_col] + j_y,
        opacity=0.12,
        color_discrete_sequence=[PALETTE["primary"]],
        labels={"x": x_label + " (jittered)", "y": "Doctor visits (jittered)"},
        title=title_str,
    )
    fig.update_layout(
        plot_bgcolor="white", yaxis_gridcolor="#E5E7EB", xaxis_gridcolor="#E5E7EB",
        margin=dict(l=5, r=5, t=40, b=5),
        title_font_size=11, title_font_color=PALETTE["muted"],
    )
    st.plotly_chart(fig, key=key)
    if notes:
        st.caption(notes)

with tab1:
    _scatter_tab(
        "reduced", "Days of reduced activity",
        jitter_x=0.25, jitter_y=0.15,
        notes=(
            "Strongest correlate with visits in this dataset. "
            "Note: value 14 is a censoring ceiling — true values beyond 14 are unknown."
        ),
        key="rel_sc_red",
    )

with tab2:
    _scatter_tab(
        "illness", "Illness count (0–5)",
        jitter_x=0.15, jitter_y=0.15,
        notes="Self-reported illness count. Not clinically coded.",
        key="rel_sc_ill",
    )

with tab3:
    _scatter_tab(
        "age_years", "Age (year band)",
        jitter_x=1.0, jitter_y=0.15,
        notes="Age is recorded in 12 discrete bands (19–72 years), not as continuous individual ages.",
        key="rel_sc_age",
    )

with tab4:
    _scatter_tab(
        "income", "Income (normalized)",
        jitter_x=0.015, jitter_y=0.15,
        notes=(
            "Very weak negative association. "
            "79 respondents have income = 0 (ambiguous — could be genuine zero or missing code)."
        ),
        key="rel_sc_inc",
    )

with tab5:
    _scatter_tab(
        "health", "Health score (0–12)",
        jitter_x=0.2, jitter_y=0.15,
        notes=(
            "Scale direction is unknown — higher may mean better or worse health. "
            "No directional interpretation is made."
        ),
        key="rel_sc_hlt",
    )
