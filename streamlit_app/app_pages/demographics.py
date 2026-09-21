"""
Demographics page — age group and gender analysis.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data_loader import PALETTE, CHART_COLORS, AGE_ORDER

dff = st.session_state["dff"]

st.title(":material/groups: Demographics")
st.caption(
    "Age group and gender patterns in the filtered dataset. "
    "All observations are associational — demographic differences do not imply biological or causal explanations."
)

if len(dff) == 0:
    st.warning("No records match the current filters.")
    st.stop()

n = len(dff)

# ── Age group summary table ───────────────────────────────────────────────────
st.subheader("Age group summary")
ag = dff.groupby("age_group").agg(
    count=("visits", "count"),
    mean_visits=("visits", "mean"),
    median_visits=("visits", "median"),
    mean_illness=("illness", "mean"),
    mean_income=("income", "mean"),
).reindex(AGE_ORDER).reset_index()
ag = ag.rename(columns={
    "age_group": "Age group",
    "count": "Respondents",
    "mean_visits": "Mean visits",
    "median_visits": "Median visits",
    "mean_illness": "Mean illness",
    "mean_income": "Mean income",
})
ag = ag.round(3)
ag["% of total"] = (ag["Respondents"] / n * 100).round(1)
st.dataframe(ag, hide_index=True)

st.divider()

# ── Row 1: age respondent counts + mean visits by age ────────────────────────
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("Respondents by age group")
        age_cnt = dff["age_group"].value_counts().reindex(AGE_ORDER).reset_index()
        age_cnt.columns = ["age_group", "count"]
        fig = px.bar(
            age_cnt, x="age_group", y="count",
            color_discrete_sequence=[PALETTE["primary"]],
            labels={"age_group": "Age group (years)", "count": "Respondents"},
            text="count",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            plot_bgcolor="white", yaxis_gridcolor="#E5E7EB",
            margin=dict(l=5, r=5, t=5, b=5),
        )
        st.plotly_chart(fig, key="dem_age_cnt")

with col2:
    with st.container(border=True):
        st.subheader("Mean visits by age group")
        age_vis = dff.groupby("age_group")["visits"].mean().reindex(AGE_ORDER).reset_index()
        age_vis.columns = ["age_group", "mean_visits"]
        fig2 = px.bar(
            age_vis, x="age_group", y="mean_visits",
            color_discrete_sequence=[PALETTE["secondary"]],
            labels={"age_group": "Age group (years)", "mean_visits": "Mean visits"},
            text=age_vis["mean_visits"].round(3),
        )
        fig2.update_traces(textposition="outside")
        fig2.update_layout(
            plot_bgcolor="white", yaxis_gridcolor="#E5E7EB",
            margin=dict(l=5, r=5, t=5, b=5),
        )
        st.plotly_chart(fig2, key="dem_age_vis")

st.divider()

# ── Gender analysis ───────────────────────────────────────────────────────────
st.subheader("Gender analysis")
st.caption(
    "The dataset records only binary gender categories (female / male). "
    "Non-binary identities are not represented."
)

col3, col4 = st.columns(2)

with col3:
    with st.container(border=True):
        st.subheader("Gender distribution")
        gd_cnt = dff["gender"].value_counts().reset_index()
        gd_cnt.columns = ["gender", "count"]
        fig3 = go.Figure(go.Pie(
            labels=gd_cnt["gender"],
            values=gd_cnt["count"],
            hole=0.4,
            marker_colors=[PALETTE["primary"], PALETTE["secondary"]],
            textinfo="percent+label",
        ))
        fig3.update_layout(
            showlegend=False,
            margin=dict(l=5, r=5, t=5, b=5),
        )
        st.plotly_chart(fig3, key="dem_gender_pie")

with col4:
    with st.container(border=True):
        st.subheader("Mean visits by gender")
        gd_vis = dff.groupby("gender")["visits"].agg(
            mean_visits="mean", count="count"
        ).reset_index()
        gd_vis["label"] = gd_vis["mean_visits"].round(3).astype(str)
        fig4 = px.bar(
            gd_vis, x="gender", y="mean_visits",
            hover_data={"count": True},
            color="gender",
            color_discrete_map={"female": PALETTE["danger"], "male": PALETTE["primary"]},
            labels={"gender": "Gender", "mean_visits": "Mean visits", "count": "Respondents"},
            text="label",
        )
        fig4.update_traces(textposition="outside")
        fig4.update_layout(
            plot_bgcolor="white", yaxis_gridcolor="#E5E7EB",
            margin=dict(l=5, r=5, t=5, b=5),
            showlegend=False,
        )
        st.plotly_chart(fig4, key="dem_gender_vis")

# ── Gender summary stats ──────────────────────────────────────────────────────
gd_stats = dff.groupby("gender")["visits"].agg(
    Respondents="count",
    Mean="mean",
    Median="median",
    Std="std",
    Max="max",
).round(3).reset_index()
gd_stats.columns = ["Gender", "Respondents", "Mean visits", "Median visits", "Std", "Max visits"]

st.markdown("**Gender comparison table**")
st.dataframe(gd_stats, hide_index=True)
st.caption(
    ":material/info: Female respondents show a higher mean visit count than male respondents "
    "in the overall dataset. This is an observed association only and may reflect other "
    "confounding factors."
)

st.divider()

# ── Age × Gender heatmap ──────────────────────────────────────────────────────
with st.container(border=True):
    st.subheader("Mean visits: age group × gender")
    pivot = dff.pivot_table(
        index="age_group", columns="gender",
        values="visits", aggfunc="mean"
    ).reindex(AGE_ORDER).round(3)

    fig5 = px.imshow(
        pivot,
        color_continuous_scale="Blues",
        aspect="auto",
        labels=dict(x="Gender", y="Age group", color="Mean visits"),
        text_auto=".3f",
    )
    fig5.update_layout(
        margin=dict(l=5, r=5, t=5, b=5),
        coloraxis_colorbar_title="Mean visits",
    )
    st.plotly_chart(fig5, key="dem_heatmap")
    st.caption(
        "Each cell shows the mean visit count for the age-group × gender combination. "
        "Lighter = lower visits, darker = higher visits."
    )
