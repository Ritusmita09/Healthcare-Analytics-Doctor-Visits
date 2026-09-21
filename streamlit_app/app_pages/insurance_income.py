"""
Insurance & Income page — insurance type, govt vs private, income groups.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from data_loader import PALETTE, CHART_COLORS, INSURANCE_ORDER, INCOME_ORDER

dff = st.session_state["dff"]

st.title(":material/account_balance: Insurance & income")
st.caption(
    "Insurance coverage and income patterns in the filtered dataset. "
    "All patterns are observational — differences between groups do not imply that "
    "insurance type or income directly causes changes in visit frequency."
)

if len(dff) == 0:
    st.warning("No records match the current filters.")
    st.stop()

n = len(dff)

# ── Insurance type ────────────────────────────────────────────────────────────
st.subheader("Insurance type")

ins_colors = {
    "Private":          PALETTE["primary"],
    "Free-Poor":        PALETTE["danger"],
    "Free-Repatriated": PALETTE["secondary"],
    "Uninsured":        PALETTE["muted"],
}

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("Insurance-type distribution")
        ins_cnt = dff["insurance_type"].value_counts().reindex(INSURANCE_ORDER).reset_index()
        ins_cnt.columns = ["type", "count"]
        ins_cnt["pct"] = (ins_cnt["count"] / n * 100).round(1)
        fig = px.bar(
            ins_cnt, x="type", y="count",
            text=ins_cnt["pct"].apply(lambda x: f"{x:.1f}%"),
            color="type",
            color_discrete_map=ins_colors,
            labels={"type": "Insurance type", "count": "Respondents"},
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            plot_bgcolor="white", yaxis_gridcolor="#E5E7EB",
            showlegend=False, margin=dict(l=5, r=5, t=5, b=5),
        )
        st.plotly_chart(fig, key="ii_ins_dist")

with col2:
    with st.container(border=True):
        st.subheader("Mean visits by insurance type")
        ins_vis = dff.groupby("insurance_type")["visits"].agg(
            mean_visits="mean", count="count"
        ).reindex(INSURANCE_ORDER).reset_index()
        fig2 = px.bar(
            ins_vis, x="insurance_type", y="mean_visits",
            hover_data={"count": True},
            color="insurance_type",
            color_discrete_map=ins_colors,
            labels={"insurance_type": "Insurance type", "mean_visits": "Mean visits"},
            text=ins_vis["mean_visits"].round(3),
        )
        fig2.update_traces(textposition="outside")
        fig2.update_layout(
            plot_bgcolor="white", yaxis_gridcolor="#E5E7EB",
            showlegend=False, margin=dict(l=5, r=5, t=5, b=5),
        )
        st.plotly_chart(fig2, key="ii_ins_vis")

# Insurance summary table
ins_tbl = dff.groupby("insurance_type")["visits"].agg(
    Respondents="count",
    Mean="mean",
    Median="median",
    Std="std",
).reindex(INSURANCE_ORDER).round(3).reset_index()
ins_tbl.columns = ["Insurance type", "Respondents", "Mean visits", "Median visits", "Std"]
st.markdown("**Insurance type comparison table**")
st.dataframe(ins_tbl, hide_index=True)
st.caption(
    ":material/info: The three insurance variables are perfectly mutually exclusive — "
    "no respondent holds more than one type."
)

st.divider()

# ── Govt-assisted vs Private ──────────────────────────────────────────────────
st.subheader("Government-assisted vs. private insurance")

govt = dff[dff["insurance_type"].isin(["Free-Poor", "Free-Repatriated"])]
priv = dff[dff["insurance_type"] == "Private"]
unin = dff[dff["insurance_type"] == "Uninsured"]

comp_data = pd.DataFrame({
    "Group": ["Govt-Assisted", "Private", "Uninsured"],
    "n": [len(govt), len(priv), len(unin)],
    "Mean visits": [govt["visits"].mean(), priv["visits"].mean(), unin["visits"].mean()],
})
comp_data["Mean visits"] = comp_data["Mean visits"].round(3)

col3, col4 = st.columns([1, 2])

with col3:
    with st.container(border=True):
        st.subheader("Group comparison")
        fig3 = px.bar(
            comp_data, x="Group", y="Mean visits",
            hover_data={"n": True},
            color="Group",
            color_discrete_sequence=[PALETTE["secondary"], PALETTE["primary"], PALETTE["muted"]],
            text="Mean visits",
        )
        fig3.update_traces(textposition="outside")
        fig3.update_layout(
            plot_bgcolor="white", yaxis_gridcolor="#E5E7EB",
            showlegend=False, margin=dict(l=5, r=5, t=5, b=5),
        )
        st.plotly_chart(fig3, key="ii_gvp")

with col4:
    st.markdown("**Group summary statistics**")
    st.dataframe(comp_data, hide_index=True)
    st.caption(
        "Government-assisted respondents (Free-Poor + Free-Repatriated) show a higher "
        "combined mean visit count than privately insured respondents. "
        "The two groups likely differ in age, health status, and income — "
        "this is an observational difference only."
    )

st.divider()

# ── Income section ────────────────────────────────────────────────────────────
st.subheader("Income level")
st.caption(
    "Income is a normalized value (0.00–1.50) with 14 discrete levels. "
    "**79 respondents have income = 0** — this may mean genuinely zero income "
    "or a missing-value code. No imputation was performed."
)

col5, col6 = st.columns(2)

with col5:
    with st.container(border=True):
        st.subheader("Income group distribution")
        inc_labels = {
            "Low(0-0.15)": "Low\n(0–0.15)",
            "Lower-Mid(0.16-0.45)": "Lower-Mid\n(0.16–0.45)",
            "Upper-Mid(0.46-0.75)": "Upper-Mid\n(0.46–0.75)",
            "High(0.76-1.50)": "High\n(0.76–1.50)",
        }
        inc_cnt = dff["income_group"].value_counts().reindex(INCOME_ORDER).reset_index()
        inc_cnt.columns = ["group", "count"]
        inc_cnt["label"] = inc_cnt["group"].map(inc_labels).fillna(inc_cnt["group"])
        inc_cnt["pct"] = (inc_cnt["count"] / n * 100).round(1)
        fig4 = px.bar(
            inc_cnt, x="label", y="count",
            text=inc_cnt["pct"].apply(lambda x: f"{x:.1f}%"),
            color_discrete_sequence=[PALETTE["secondary"]],
            labels={"label": "Income group", "count": "Respondents"},
        )
        fig4.update_traces(textposition="outside")
        fig4.update_layout(
            plot_bgcolor="white", yaxis_gridcolor="#E5E7EB",
            margin=dict(l=5, r=5, t=5, b=5),
        )
        st.plotly_chart(fig4, key="ii_inc_dist")

with col6:
    with st.container(border=True):
        st.subheader("Mean visits by income group")
        inc_vis = dff.groupby("income_group")["visits"].agg(
            mean_visits="mean", count="count"
        ).reindex(INCOME_ORDER).reset_index()
        inc_vis["label"] = inc_vis["income_group"].map(inc_labels).fillna(inc_vis["income_group"])
        fig5 = px.bar(
            inc_vis, x="label", y="mean_visits",
            hover_data={"count": True},
            color_discrete_sequence=[PALETTE["secondary"]],
            labels={"label": "Income group", "mean_visits": "Mean visits"},
            text=inc_vis["mean_visits"].round(3),
        )
        fig5.update_traces(textposition="outside")
        fig5.update_layout(
            plot_bgcolor="white", yaxis_gridcolor="#E5E7EB",
            margin=dict(l=5, r=5, t=5, b=5),
        )
        st.plotly_chart(fig5, key="ii_inc_vis")

# ── Income scatter ────────────────────────────────────────────────────────────
with st.container(border=True):
    st.subheader("Income (continuous) vs. doctor visits")
    rng = np.random.RandomState(99)
    j1 = rng.uniform(-0.015, 0.015, len(dff))
    j2 = rng.uniform(-0.15, 0.15, len(dff))
    fig6 = px.scatter(
        x=dff["income"] + j1,
        y=dff["visits"] + j2,
        opacity=0.12,
        color_discrete_sequence=[PALETTE["secondary"]],
        labels={"x": "Income (normalized, jittered)", "y": "Doctor visits (jittered)"},
    )
    fig6.add_vline(x=0, line_dash="dot", line_color="red",
                   annotation_text="income=0 (n=79)", annotation_position="top right")
    fig6.update_layout(
        plot_bgcolor="white",
        yaxis_gridcolor="#E5E7EB",
        xaxis_gridcolor="#E5E7EB",
        margin=dict(l=5, r=5, t=5, b=5),
    )
    st.plotly_chart(fig6, key="ii_inc_scatter")
    st.caption(
        "Spearman rho ≈ −0.093 (full dataset) — a very weak negative association. "
        "Lower income tiers show slightly higher mean visits. "
        "The practical effect size is small."
    )
