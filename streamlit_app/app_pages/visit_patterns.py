"""
Visit Patterns page — distributions, boxplot, illness vs visits, reduced vs visits.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from data_loader import PALETTE, CHART_COLORS, VISIT_GRP_ORDER

dff = st.session_state["dff"]

st.title(":material/bar_chart: Visit patterns")
st.caption(
    "Distribution of doctor visits in the filtered population. "
    "The dataset is heavily zero-inflated and right-skewed."
)

if len(dff) == 0:
    st.warning("No records match the current filters.")
    st.stop()

n = len(dff)

# ── Visit stats ───────────────────────────────────────────────────────────────
with st.container(horizontal=True):
    st.metric("Mean",     f"{dff['visits'].mean():.3f}", border=True)
    st.metric("Median",   f"{dff['visits'].median():.0f}", border=True)
    st.metric("Std dev",  f"{dff['visits'].std():.3f}", border=True)
    st.metric("Max",      f"{dff['visits'].max()}", border=True)
    st.metric("Skewness", f"{dff['visits'].skew():.2f}", border=True)

st.divider()

# ── Row 1: histogram + boxplot ────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("Visit count histogram")
        vc = dff["visits"].value_counts().sort_index().reset_index()
        vc.columns = ["visits", "count"]
        fig = px.bar(
            vc, x="visits", y="count",
            color_discrete_sequence=[PALETTE["primary"]],
            labels={"visits": "Number of visits", "count": "Respondents"},
        )
        fig.update_layout(
            plot_bgcolor="white", yaxis_gridcolor="#E5E7EB",
            margin=dict(l=5, r=5, t=5, b=5),
        )
        st.plotly_chart(fig, key="vp_hist")

with col2:
    with st.container(border=True):
        st.subheader("Doctor visits — boxplot")
        fig2 = go.Figure()
        fig2.add_trace(go.Box(
            y=dff["visits"],
            name="Visits",
            marker_color=PALETTE["primary"],
            boxpoints="outliers",
            line_color=PALETTE["primary"],
        ))
        fig2.update_layout(
            plot_bgcolor="white", yaxis_gridcolor="#E5E7EB",
            margin=dict(l=5, r=5, t=5, b=5),
            yaxis_title="Number of visits",
            showlegend=False,
        )
        st.plotly_chart(fig2, key="vp_box")

# ── Row 2: non-zero histogram + visit group bar ───────────────────────────────
col3, col4 = st.columns(2)

with col3:
    with st.container(border=True):
        st.subheader("Non-zero visit distribution")
        nz = dff[dff["visits"] > 0]["visits"].value_counts().sort_index().reset_index()
        nz.columns = ["visits", "count"]
        if len(nz) == 0:
            st.info("No non-zero visits in the current selection.")
        else:
            fig3 = px.bar(
                nz, x="visits", y="count",
                color_discrete_sequence=[PALETTE["secondary"]],
                labels={"visits": "Visits (non-zero)", "count": "Respondents"},
            )
            fig3.update_layout(
                plot_bgcolor="white", yaxis_gridcolor="#E5E7EB",
                margin=dict(l=5, r=5, t=5, b=5),
            )
            st.plotly_chart(fig3, key="vp_nz")

with col4:
    with st.container(border=True):
        st.subheader("Visit group distribution")
        vg = dff["visit_group"].value_counts().reindex(VISIT_GRP_ORDER).reset_index()
        vg.columns = ["group", "count"]
        vg["pct"] = (vg["count"] / n * 100).round(1)
        fig4 = px.bar(
            vg, x="group", y="count",
            text=vg["pct"].apply(lambda x: f"{x:.1f}%"),
            color_discrete_sequence=[PALETTE["accent"]],
            labels={"group": "Visit group", "count": "Respondents"},
        )
        fig4.update_traces(textposition="outside")
        fig4.update_layout(
            plot_bgcolor="white", yaxis_gridcolor="#E5E7EB",
            margin=dict(l=5, r=5, t=5, b=5),
        )
        st.plotly_chart(fig4, key="vp_vg")

st.divider()

# ── Average visits by illness count ──────────────────────────────────────────
with st.container(border=True):
    st.subheader("Mean visits by illness count")
    st.caption("Respondents self-reported the number of illnesses in the past 2 weeks (0–5).")
    ill_mean = dff.groupby("illness")["visits"].agg(
        mean_visits="mean", count="count"
    ).reset_index()
    fig5 = px.bar(
        ill_mean, x="illness", y="mean_visits",
        hover_data={"count": True},
        color_discrete_sequence=[PALETTE["danger"]],
        labels={"illness": "Illness count", "mean_visits": "Mean visits", "count": "Respondents"},
        text=ill_mean["mean_visits"].round(3),
    )
    fig5.update_traces(textposition="outside")
    fig5.update_layout(
        plot_bgcolor="white", yaxis_gridcolor="#E5E7EB",
        margin=dict(l=5, r=5, t=40, b=5),
    )
    st.plotly_chart(fig5, key="vp_ill")
    st.caption(
        ":material/info: This chart shows an observed association only. "
        "Higher illness counts are associated with higher mean visits. "
        "This does not establish causation."
    )

st.divider()

# ── Reduced-activity days vs visits ──────────────────────────────────────────
with st.container(border=True):
    st.subheader("Reduced-activity days vs. doctor visits")
    st.caption(
        "Days of reduced activity in the past 2 weeks (0–14). "
        "Value **14** is a measurement ceiling — it means '14 or more days'."
    )

    col5, col6 = st.columns([1, 2])

    with col5:
        df_tier = dff.copy()
        df_tier["tier"] = pd.cut(
            df_tier["reduced"], bins=[-1, 0, 3, 7, 14],
            labels=["0 days", "1-3 days", "4-7 days", "8-14 days"]
        )
        rt = df_tier.groupby("tier")["visits"].agg(
            mean_visits="mean", count="count"
        ).reset_index()
        fig6 = px.bar(
            rt, x="tier", y="mean_visits",
            hover_data={"count": True},
            color_discrete_sequence=[PALETTE["accent"]],
            labels={"tier": "Reduced-activity tier", "mean_visits": "Mean visits"},
            text=rt["mean_visits"].round(3),
        )
        fig6.update_traces(textposition="outside")
        fig6.update_layout(
            plot_bgcolor="white", yaxis_gridcolor="#E5E7EB",
            margin=dict(l=5, r=5, t=10, b=5),
        )
        st.plotly_chart(fig6, key="vp_red_bar")

    with col6:
        # Jittered scatter
        rng = np.random.RandomState(42)
        jitter = rng.uniform(-0.25, 0.25, len(dff))
        fig7 = px.scatter(
            x=dff["reduced"] + jitter,
            y=dff["visits"],
            opacity=0.15,
            color_discrete_sequence=[PALETTE["primary"]],
            labels={"x": "Days of reduced activity (jittered)", "y": "Doctor visits"},
        )
        fig7.add_vline(x=14, line_dash="dash", line_color="red",
                       annotation_text="Ceiling (14)", annotation_position="top right")
        fig7.update_layout(
            plot_bgcolor="white", yaxis_gridcolor="#E5E7EB",
            xaxis_gridcolor="#E5E7EB",
            margin=dict(l=5, r=5, t=10, b=5),
        )
        st.plotly_chart(fig7, key="vp_red_scatter")

# ── Distribution description ──────────────────────────────────────────────────
with st.expander(":material/info: About the zero-inflated distribution"):
    st.markdown(
        f"""
        **Zero inflation:** {(dff['visits'] == 0).mean()*100:.1f}% of respondents in the current
        selection report zero doctor visits.  
        
        **Right skew:** A small number of respondents report high visit counts (up to {dff['visits'].max()}).  
        
        **IQR note:** Because ≥75% of respondents have 0 visits, the interquartile range (IQR) = 0.
        Standard IQR-based outlier removal is **not appropriate** for this distribution.
        High visit values are preserved as legitimate survey responses.
        """
    )
