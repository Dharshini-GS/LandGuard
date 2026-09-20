"""
Explainable AI (SHAP) Page for VISTRA.
Features interactive Plotly Waterfall Attribution Chart & Feature Sensitivity Analysis.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from frontend.utils import fetch_filtered_projects
from backend.services.ml_service import ml_service_instance

def render_explainable_ai_page(user: dict):
    st.markdown("## Explainable AI (SHAP Feature Attribution)")

    projects = fetch_filtered_projects(user, limit=200)
    if not projects:
        st.info("No projects available within your scope.")
        return

    p_ids = [p["project_id"] for p in projects]
    default_pid = st.session_state.get("selected_project_id", p_ids[0] if p_ids else "")
    if default_pid not in p_ids:
        default_pid = p_ids[0]

    selected_pid = st.selectbox("Select Project for SHAP Explanation:", p_ids, index=p_ids.index(default_pid), key="shap_proj_select")
    st.session_state["selected_project_id"] = selected_pid

    shap_info = ml_service_instance.explain_shap(selected_pid)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Predicted Delay Prob", f"{shap_info['delay_probability']*100:.1f}%")
    c2.metric("Risk Category", shap_info["risk_category"])
    c3.metric("Base Expected Prob", f"{shap_info['base_value']*100:.1f}%")
    c4.metric("Active Drivers", f"{len(shap_info['top_contributors'])} Factors")

    st.markdown(f"""
    <div class="kpi-card" style="background-color:#F8FAFC; border-left:4px solid #0284C7;">
        <b>AI Diagnostic Summary:</b><br/>
        {shap_info['summary_human']}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # 1. Interactive Plotly Waterfall Chart
    st.subheader("Step-by-Step Probability Waterfall Attribution")

    factors = shap_info["top_contributors"][:7]  # Top 7 factors
    base_val = shap_info["base_value"] * 100.0

    measure = ["relative"] * len(factors)
    x_labels = [f["human_label"] for f in factors]
    y_values = [f["shap_value"] * 100.0 for f in factors]

    fig_waterfall = go.Figure(go.Waterfall(
        name="SHAP Impact",
        orientation="v",
        measure=measure,
        x=x_labels,
        textposition="outside",
        text=[f"{v:+.1f}%" for v in y_values],
        y=y_values,
        connector={"line": {"color": "#94A3B8"}},
        decreasing={"marker": {"color": "#16A34A"}},
        increasing={"marker": {"color": "#DC2626"}}
    ))

    fig_waterfall.update_layout(
        title="Cumulative Risk Probability Additions / Deductions",
        waterfallgap=0.3,
        height=400,
        margin=dict(t=30, b=30, l=20, r=20),
        xaxis_tickangle=-25
    )

    st.plotly_chart(fig_waterfall, use_container_width=True)

    st.markdown("---")

    # 2. Feature Impact Evidence Matrix
    st.subheader("Top Contributing Factor Evidence")
    for f in factors:
        direction_label = "Increases Risk" if f["impact_direction"] == "INCREASES_RISK" else "Reduces Risk"
        badge_color = "#991B1B" if f["impact_direction"] == "INCREASES_RISK" else "#15803D"
        st.markdown(f"""
        <div class="kpi-card" style="margin-bottom:8px; padding:12px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <b>{f['human_label']}</b>
                <span style="font-size:11px; font-weight:700; color:{badge_color};">
                    SHAP Delta: {f['shap_value']:+.4f} ({direction_label})
                </span>
            </div>
            <div style="font-size:12px; color:#4B5563; margin-top:4px;">
                Metric Value: <b>{f['feature_value']}</b> | {f['explanation']}
            </div>
        </div>
        """, unsafe_allow_html=True)
