"""
Scope-Aware Analytics & Bottlenecks Page for LANDGUARD AI.
Clean professional analytical plots.
"""

import streamlit as st
import plotly.express as px
import pandas as pd

from frontend.utils import fetch_filtered_projects

def render_analytics_page(user: dict):
    st.markdown("## Macro Analytics & Bottleneck Diagnostics")

    projects = fetch_filtered_projects(user, limit=500)
    if not projects:
        st.info("No data available within your scope.")
        return

    df = pd.DataFrame(projects)

    st.markdown("### 1. Risk Profile & Expected Delay Scatter")
    fig_scat = px.scatter(
        df,
        x="risk_score",
        y="expected_delay_days",
        color="risk_category",
        hover_data=["project_id", "project_name", "state_name", "district_name"],
        color_discrete_map={"CRITICAL": "#DC2626", "HIGH": "#EA580C", "MEDIUM": "#D97706", "LOW": "#16A34A"},
        labels={"risk_score": "Risk Score (%)", "expected_delay_days": "Expected Completion Delay (Days)"}
    )
    fig_scat.update_layout(height=360)
    st.plotly_chart(fig_scat, use_container_width=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### 2. Risk Distribution by Sector")
        sec_df = df.groupby(["project_type", "risk_category"])["project_id"].count().reset_index()
        fig_sec = px.bar(
            sec_df,
            x="project_type",
            y="project_id",
            color="risk_category",
            barmode="stack",
            color_discrete_map={"CRITICAL": "#DC2626", "HIGH": "#EA580C", "MEDIUM": "#D97706", "LOW": "#16A34A"},
            labels={"project_type": "Sector", "project_id": "Projects Count"}
        )
        fig_sec.update_layout(height=320, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_sec, use_container_width=True)

    with col_b:
        st.markdown("### 3. Stage Bottlenecks")
        stg_df = df.groupby("current_stage")["risk_score"].mean().reset_index().sort_values("risk_score", ascending=False)
        fig_stg = px.bar(stg_df, x="current_stage", y="risk_score", color="risk_score", color_continuous_scale="Purples")
        fig_stg.update_layout(height=320, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_stg, use_container_width=True)
