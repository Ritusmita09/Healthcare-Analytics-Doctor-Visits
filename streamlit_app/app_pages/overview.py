"""
Overview page — KPI cards, visit distribution, dataset summary.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from data_loader import CHART_COLORS, PALETTE

df  = st.session_state["df"]
dff = st.session_state["dff"]

# ── Title ─────────────────────────────────────────────────────────────────────
st.title(":material/dashboard: Overview")
st.caption(
    "Summary of the Healthcare Doctor Visits dataset. "
    "All metrics update dynamically when sidebar filters are applied."
)

if len(dff) == 0:
    st.warning("No records match the selected filters. Please adjust the sidebar filters.")
    st.stop()

# ── KPI calculations ──────────────────────────────────────────────────────────
n          = len(dff)
mean_vis   = dff["visits"].mean()
med_vis    = dff["visits"].median()
zero_pct   = (dff["visits"] == 0).mean() * 100
mean_age   = dff["age_years"].mean()
mean_ill   = dff["illness"].mean()
mean_red   = dff["reduced"].mean()
high_util  = (dff["visits"] >= 3).sum()

# ── KPI row ───────────────────────────────────────────────────────────────────
with st.container(horizontal=True):
    st.metric("Respondents",          f"{n:,}",          border=True)
    st.metric("Mean visits",          f"{mean_vis:.3f}",  border=True)
    st.metric("Median visits",        f"{med_vis:.0f}",   border=True)
    st.metric("Zero-visit %",         f"{zero_pct:.1f}%", border=True)

with st.container(horizontal=True):
    st.metric("Mean age (years)",     f"{mean_age:.1f}",  border=True)
    st.metric("Mean illness count",   f"{mean_ill:.2f}",  border=True)
    st.metric("Mean reduced-activity days", f"{mean_red:.2f}", border=True)
    st.metric("High utilizers (≥3 visits)", f"{high_util:,}", border=True)

st.divider()

# ── Charts row ────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

# Visit count distribution
with col1:
    with st.container(border=True):
        st.subheader("Visit count distribution")
        vc = dff["visits"].value_counts().sort_index().reset_index()
        vc.columns = ["visits", "count"]
        fig = px.bar(
            vc, x="visits", y="count",
            color_discrete_sequence=[PALETTE["primary"]],
            labels={"visits": "Number of visits", "count": "Respondents"},
        )
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="white",
            yaxis_gridcolor="#E5E7EB",
        )
        st.plotly_chart(fig, key="ov_hist")

# Zero vs non-zero pie
with col2:
    with st.container(border=True):
        st.subheader("Zero vs. non-zero visits")
        n_zero = (dff["visits"] == 0).sum()
        n_nonz = n - n_zero
        fig2 = go.Figure(go.Pie(
            labels=["Zero visits", "1+ visits"],
            values=[n_zero, n_nonz],
            hole=0.45,
            marker_colors=[PALETTE["primary"], PALETTE["secondary"]],
            textinfo="percent+label",
        ))
        fig2.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
        )
        st.plotly_chart(fig2, key="ov_pie")

st.divider()

# ── Visit group bar ───────────────────────────────────────────────────────────
with st.container(border=True):
    st.subheader("Visit group distribution")
    vg_order = ["0 visits", "1-2 visits", "3-5 visits", "6+ visits"]
    vg = dff["visit_group"].value_counts().reindex(vg_order).reset_index()
    vg.columns = ["group", "count"]
    vg["pct"] = (vg["count"] / n * 100).round(1)
    fig3 = px.bar(
        vg, x="group", y="count",
        text=vg["pct"].apply(lambda x: f"{x}%"),
        color_discrete_sequence=[PALETTE["primary"]],
        labels={"group": "Visit group", "count": "Respondents"},
    )
    fig3.update_traces(textposition="outside")
    fig3.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="white",
        yaxis_gridcolor="#E5E7EB",
    )
    st.plotly_chart(fig3, key="ov_vg")

st.divider()

# ── Evidence-based note ───────────────────────────────────────────────────────
with st.expander(":material/info: About this dataset and analysis", expanded=False):
    st.markdown(
        f"""
        **Dataset:** Healthcare Doctor Visits Survey · {len(df):,} total respondents  
        **Processed columns:** 26 (12 original + 14 engineered)  
        **Missing values:** 0  

        This dashboard presents **descriptive associations only**.  
        All findings are observational — no causal relationships are established.  
        The dataset is zero-inflated: **{(df['visits']==0).mean()*100:.1f}%** of respondents report zero visits.  
        Most group-level medians equal 0; differences are visible in the means and right tail.

        > *"Correlation indicates association and does not establish causation."*
        """
    )
