"""
Health Burden page — illness, chronic conditions, reduced activity, health score.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from data_loader import PALETTE, CHART_COLORS, CHRONIC_ORDER

dff = st.session_state["dff"]

st.title(":material/medical_information: Health burden")
st.caption(
    "Observed associations between health-burden variables and doctor visit frequency. "
    "All findings are descriptive and observational."
)

if len(dff) == 0:
    st.warning("No records match the current filters.")
    st.stop()

# ── Chronic status summary ────────────────────────────────────────────────────
st.subheader("Chronic condition status")
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("Chronic-status distribution")
        cs_cnt = dff["chronic_status"].value_counts().reindex(CHRONIC_ORDER).reset_index()
        cs_cnt.columns = ["status", "count"]
        cs_cnt["pct"] = (cs_cnt["count"] / len(dff) * 100).round(1)
        fig = px.bar(
            cs_cnt, x="status", y="count",
            text=cs_cnt["pct"].apply(lambda x: f"{x:.1f}%"),
            color="status",
            color_discrete_sequence=[PALETTE["secondary"], PALETTE["accent"], PALETTE["danger"]],
            labels={"status": "Chronic status", "count": "Respondents"},
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            plot_bgcolor="white", yaxis_gridcolor="#E5E7EB",
            showlegend=False, margin=dict(l=5, r=5, t=5, b=5),
        )
        st.plotly_chart(fig, key="hb_cs_dist")

with col2:
    with st.container(border=True):
        st.subheader("Mean visits by chronic status")
        cs_vis = dff.groupby("chronic_status")["visits"].agg(
            mean_visits="mean", count="count"
        ).reindex(CHRONIC_ORDER).reset_index()
        fig2 = px.bar(
            cs_vis, x="chronic_status", y="mean_visits",
            hover_data={"count": True},
            color="chronic_status",
            color_discrete_sequence=[PALETTE["secondary"], PALETTE["accent"], PALETTE["danger"]],
            labels={"chronic_status": "Chronic status", "mean_visits": "Mean visits"},
            text=cs_vis["mean_visits"].round(3),
        )
        fig2.update_traces(textposition="outside")
        fig2.update_layout(
            plot_bgcolor="white", yaxis_gridcolor="#E5E7EB",
            showlegend=False, margin=dict(l=5, r=5, t=5, b=5),
        )
        st.plotly_chart(fig2, key="hb_cs_vis")

st.caption(
    ":material/info: Limiting chronic conditions (functional limitation) are associated "
    "with the highest mean visit count. This is an observed association — chronic conditions "
    "may co-occur with other factors that influence visit frequency."
)

st.divider()

# ── Illness count section ─────────────────────────────────────────────────────
st.subheader("Illness count vs. visits")
st.caption("Number of self-reported illnesses in the past 2 weeks (0–5). Not clinically coded.")

col3, col4 = st.columns(2)

with col3:
    with st.container(border=True):
        st.subheader("Illness distribution")
        ill_cnt = dff["illness"].value_counts().sort_index().reset_index()
        ill_cnt.columns = ["illness", "count"]
        fig3 = px.bar(
            ill_cnt, x="illness", y="count",
            color_discrete_sequence=[PALETTE["danger"]],
            labels={"illness": "Illness count", "count": "Respondents"},
            text="count",
        )
        fig3.update_traces(textposition="outside")
        fig3.update_layout(
            plot_bgcolor="white", yaxis_gridcolor="#E5E7EB",
            margin=dict(l=5, r=5, t=5, b=5),
        )
        st.plotly_chart(fig3, key="hb_ill_dist")

with col4:
    with st.container(border=True):
        st.subheader("Mean visits by illness count")
        ill_vis = dff.groupby("illness")["visits"].agg(
            mean_visits="mean", count="count"
        ).reset_index()
        fig4 = px.bar(
            ill_vis, x="illness", y="mean_visits",
            hover_data={"count": True},
            color_discrete_sequence=[PALETTE["danger"]],
            labels={"illness": "Illness count", "mean_visits": "Mean visits"},
            text=ill_vis["mean_visits"].round(3),
        )
        fig4.update_traces(textposition="outside")
        fig4.update_layout(
            plot_bgcolor="white", yaxis_gridcolor="#E5E7EB",
            margin=dict(l=5, r=5, t=5, b=5),
        )
        st.plotly_chart(fig4, key="hb_ill_vis")

st.divider()

# ── Reduced activity section ──────────────────────────────────────────────────
st.subheader("Reduced-activity days vs. visits")
st.caption(
    "Days of reduced activity in the past 2 weeks (0–14). "
    "Value **14** is a measurement ceiling (14 or more days)."
)

col5, col6 = st.columns([1, 2])

with col5:
    with st.container(border=True):
        st.subheader("Mean visits by activity tier")
        df_tier = dff.copy()
        df_tier["tier"] = pd.cut(
            df_tier["reduced"], bins=[-1, 0, 3, 7, 14],
            labels=["0 days", "1-3 days", "4-7 days", "8-14 days"]
        )
        rt = df_tier.groupby("tier")["visits"].agg(
            mean_visits="mean", count="count"
        ).reset_index()
        fig5 = px.bar(
            rt, x="tier", y="mean_visits",
            hover_data={"count": True},
            color_discrete_sequence=[PALETTE["accent"]],
            labels={"tier": "Reduced-activity tier", "mean_visits": "Mean visits"},
            text=rt["mean_visits"].round(3),
        )
        fig5.update_traces(textposition="outside")
        fig5.update_layout(
            plot_bgcolor="white", yaxis_gridcolor="#E5E7EB",
            margin=dict(l=5, r=5, t=5, b=5),
        )
        st.plotly_chart(fig5, key="hb_red_bar")

with col6:
    with st.container(border=True):
        st.subheader("Reduced activity distribution")
        red_cnt = dff["reduced"].value_counts().sort_index().reset_index()
        red_cnt.columns = ["reduced", "count"]
        fig6 = px.bar(
            red_cnt, x="reduced", y="count",
            color_discrete_sequence=[PALETTE["accent"]],
            labels={"reduced": "Days of reduced activity", "count": "Respondents"},
        )
        fig6.add_vline(
            x=14, line_dash="dash", line_color="red",
            annotation_text="Ceiling (14 days)",
            annotation_position="top left",
        )
        fig6.update_layout(
            plot_bgcolor="white", yaxis_gridcolor="#E5E7EB",
            margin=dict(l=5, r=5, t=5, b=5),
        )
        st.plotly_chart(fig6, key="hb_red_dist")

st.divider()

# ── Health score section ──────────────────────────────────────────────────────
st.subheader("Health score vs. visits")
st.warning(
    ":material/warning: **Scale direction unknown.** "
    "The health score (0–12) scale direction is not documented. "
    "Higher values may mean better *or* worse health. "
    "No directional interpretation is made.",
    icon=":material/info:",
)

col7, col8 = st.columns(2)

with col7:
    with st.container(border=True):
        st.subheader("Health score distribution")
        hs_cnt = dff["health"].value_counts().sort_index().reset_index()
        hs_cnt.columns = ["health", "count"]
        fig7 = px.bar(
            hs_cnt, x="health", y="count",
            color_discrete_sequence=[PALETTE["primary"]],
            labels={"health": "Health score", "count": "Respondents"},
        )
        fig7.update_layout(
            plot_bgcolor="white", yaxis_gridcolor="#E5E7EB",
            margin=dict(l=5, r=5, t=5, b=5),
        )
        st.plotly_chart(fig7, key="hb_hs_dist")

with col8:
    with st.container(border=True):
        st.subheader("Mean visits by health score")
        hs_vis = dff.groupby("health")["visits"].agg(
            mean_visits="mean", count="count"
        ).reset_index()
        fig8 = px.bar(
            hs_vis, x="health", y="mean_visits",
            hover_data={"count": True},
            color_discrete_sequence=[PALETTE["primary"]],
            labels={"health": "Health score (direction unknown)", "mean_visits": "Mean visits"},
        )
        fig8.update_layout(
            plot_bgcolor="white", yaxis_gridcolor="#E5E7EB",
            margin=dict(l=5, r=5, t=5, b=5),
        )
        st.plotly_chart(fig8, key="hb_hs_vis")

st.caption(
    "Spearman rho ≈ 0.178 between health score and visits (calculated on full dataset). "
    "This indicates a weak positive monotonic association. "
    "Without knowing the scale direction, no directional medical interpretation is made."
)
