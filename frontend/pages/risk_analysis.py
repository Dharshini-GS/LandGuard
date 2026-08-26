"""
Risk Analysis & Trends Page for LANDGUARD AI.
"""

import streamlit as st
import plotly.express as px
import pandas as pd

from frontend.utils import fetch_filtered_projects

def render_risk_analysis_page(user: dict):
    st.markdown("## Risk Assessment & Trend Analysis")

    projects = fetch_filtered_projects(user, limit=300)
    if not projects:
        st.info("No projects available within your authorized scope.")
        return

    df = pd.DataFrame(projects)

    st.markdown("#### Project Risk Score Ranking")

    fig = px.histogram(
        df,
        x="risk_score",
        nbins=20,
        color="risk_category",
        color_discrete_map={"CRITICAL": "#DC2626", "HIGH": "#EA580C", "MEDIUM": "#D97706", "LOW": "#16A34A"},
        labels={"risk_score": "Delay Probability Risk Score (%)", "count": "Project Count"}
    )
    fig.update_layout(height=320, margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("High Risk Project Directory")

    high_risk_df = df[df["risk_category"].isin(["CRITICAL", "HIGH"])].sort_values("risk_score", ascending=False)
    st.dataframe(
        high_risk_df[["project_id", "project_name", "state_name", "district_name", "current_stage", "risk_category", "risk_score", "expected_delay_days"]],
        use_container_width=True,
        hide_index=True
    )
