"""
What-If Scenario Simulator Page for VISTRA.
Features real-time feature tweaking, Plotly comparative charts, and benchmark scenario comparisons.
"""

import streamlit as st
import sqlite3
import json
import uuid
from datetime import datetime
import plotly.graph_objects as go
import pandas as pd

from frontend.utils import fetch_filtered_projects
from backend.services.ml_service import ml_service_instance
from backend.database import execute_query_one, execute_write, execute_query
from backend.services.audit_service import log_action

def render_what_if_page(user: dict):
    st.markdown("## Interactive What-If Scenario Simulator")

    projects = fetch_filtered_projects(user, limit=200)
    if not projects:
        st.info("No projects available within your scope.")
        return

    p_ids = [p["project_id"] for p in projects]
    default_pid = st.session_state.get("selected_project_id", p_ids[0] if p_ids else "")
    if default_pid not in p_ids:
        default_pid = p_ids[0]

    selected_pid = st.selectbox("Select Project for Simulation:", p_ids, index=p_ids.index(default_pid), key="sim_proj_select")
    st.session_state["selected_project_id"] = selected_pid

    # Fetch initial baseline metrics
    init_res = ml_service_instance.predict_risk(selected_pid)
    row = ml_service_instance.fetch_project_feature_row(selected_pid)

    st.markdown(f"#### Project Baseline: `{selected_pid}` | Initial Risk: **{init_res['risk_score']:.1f}% ({init_res['risk_category']})**")

    st.markdown("---")
    st.subheader("Simulate Interventions & Policy Tweaks")

    c1, c2 = st.columns(2)

    with c1:
        cur_comp = float(row.get("compensation_completion_percentage") or 42.0)
        sim_comp = st.slider(
            "Compensation Disbursement Completion (%)",
            min_value=0.0, max_value=100.0, value=cur_comp, step=1.0,
            key="sim_slider_comp"
        )

        cur_cases = int(row.get("pending_cases") or 14)
        sim_cases = st.slider(
            "Pending Legal Court Cases (Count)",
            min_value=0, max_value=50, value=cur_cases, step=1,
            key="sim_slider_legal"
        )

        cur_app = int(row.get("approval_delay_score") or 90)
        sim_app = st.slider(
            "Statutory Clearance Delay (Days)",
            min_value=0, max_value=180, value=cur_app, step=5,
            key="sim_slider_app"
        )

    with c2:
        cur_doc = float(row.get("documentation_completion_percentage") or 70.0)
        sim_doc = st.slider(
            "Land Title Clearance & Verification (%)",
            min_value=0.0, max_value=100.0, value=cur_doc, step=1.0,
            key="sim_slider_doc"
        )

        cur_rr = float(row.get("rr_completion_score") or 35.0)
        sim_rr = st.slider(
            "R&R Resettlement Site Readiness (%)",
            min_value=0.0, max_value=100.0, value=cur_rr, step=1.0,
            key="sim_slider_rr"
        )

        cur_stk = float(row.get("stakeholder_response_score") or 38.0)
        sim_stk = st.slider(
            "Community Opposition Index (0-100)",
            min_value=0.0, max_value=100.0, value=cur_stk, step=1.0,
            key="sim_slider_stk"
        )

    st.markdown("---")

    if st.button("Calculate Simulated Risk Outcome", type="primary", use_container_width=True, key="btn_run_sim_calc"):
        mods = {
            "compensation_completion_pct": sim_comp,
            "pending_legal_cases": sim_cases,
            "approval_delay_days": sim_app,
            "documentation_completion_pct": sim_doc,
            "rr_completion_pct": sim_rr,
            "stakeholder_response_idx": sim_stk
        }

        # Run model simulation
        sim_res = ml_service_instance.simulate_what_if(selected_pid, mods)

        # Record simulation
        sim_id = f"SIM-{uuid.uuid4().hex[:8].upper()}"
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        execute_write("""
        INSERT INTO simulations (sim_id, project_id, user_id, parameters_json, initial_risk_score, simulated_risk_score, risk_reduction, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sim_id, selected_pid, user["user_id"], json.dumps(mods),
            sim_res["initial_risk_score"], sim_res["simulated_risk_score"],
            sim_res["risk_reduction"], ts
        ))
        log_action(user, "RUN_SIMULATION", project_id=selected_pid, details=f"Simulated risk reduction: {sim_res['risk_reduction']}%")

        st.success("Simulation Complete!")

        # Results metrics
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Current Risk", f"{sim_res['initial_risk_score']:.1f}%", delta=sim_res['initial_risk_category'])
        k2.metric("Simulated Risk", f"{sim_res['simulated_risk_score']:.1f}%", delta=sim_res['simulated_risk_category'])

        delta_color = "normal" if sim_res['risk_reduction'] > 0 else "inverse"
        k3.metric("Net Risk Reduction", f"{sim_res['risk_reduction']:+.1f}%", delta=f"{sim_res['risk_reduction']:.1f} Percentage Points", delta_color=delta_color)
        k4.metric("Simulated Delay", f"{sim_res['simulated_expected_delay_days']} Days")

        st.markdown("---")

        # Comparative Bar Chart
        st.subheader("Baseline vs. Simulated Risk Comparison")
        fig_comp = go.Figure(data=[
            go.Bar(name="Initial Baseline Risk", x=["Delay Risk (%)", "Expected Delay (Days)"], y=[sim_res["initial_risk_score"], init_res["expected_delay_days"]], marker_color="#DC2626"),
            go.Bar(name="Simulated Policy Risk", x=["Delay Risk (%)", "Expected Delay (Days)"], y=[sim_res["simulated_risk_score"], sim_res["simulated_expected_delay_days"]], marker_color="#0284C7")
        ])
        fig_comp.update_layout(barmode="group", height=320, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_comp, use_container_width=True)

        st.caption(f"Note: {sim_res['disclaimer']}")

    # Benchmark History Table for this project
    st.markdown("---")
    st.subheader("Saved Policy Simulation Benchmarks")
    saved_sims = execute_query("""
    SELECT sim_id, initial_risk_score, simulated_risk_score, risk_reduction, created_at
    FROM simulations
    WHERE project_id = ?
    ORDER BY created_at DESC
    LIMIT 5
    """, (selected_pid,))

    if saved_sims:
        st.dataframe(pd.DataFrame(saved_sims), use_container_width=True, hide_index=True)
