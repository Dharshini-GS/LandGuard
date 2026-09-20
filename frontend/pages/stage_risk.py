"""
Stage-Wise Risk Analysis Page for VISTRA.
Clean professional lifecycle stage breakdown.
"""

import streamlit as st
import plotly.express as px
import pandas as pd

from frontend.utils import fetch_filtered_projects
from backend.services.ml_service import ml_service_instance
from utils.geo_data import LIFECYCLE_STAGES
from backend.database import execute_query_one

def render_stage_risk_page(user: dict):
    st.markdown("## 11-Stage Lifecycle Risk Breakdown")

    projects = fetch_filtered_projects(user, limit=200)
    if not projects:
        st.info("No projects available within your scope.")
        return

    p_ids = [p["project_id"] for p in projects]
    default_pid = st.session_state.get("selected_project_id", p_ids[0] if p_ids else "")
    if default_pid not in p_ids:
        default_pid = p_ids[0]

    selected_pid = st.selectbox("Select Project to Analyze Stage-wise Risk:", p_ids, index=p_ids.index(default_pid), key="stg_proj_select")
    st.session_state["selected_project_id"] = selected_pid

    proj = execute_query_one("SELECT * FROM projects WHERE project_id = ?", (selected_pid,))
    comp = execute_query_one("SELECT * FROM compensation WHERE project_id = ?", (selected_pid,))
    legal = execute_query_one("SELECT * FROM legal_disputes WHERE project_id = ?", (selected_pid,))
    doc = execute_query_one("SELECT * FROM documentation WHERE project_id = ?", (selected_pid,))
    app = execute_query_one("SELECT * FROM approvals WHERE project_id = ?", (selected_pid,))
    rr = execute_query_one("SELECT * FROM rehabilitation_rr WHERE project_id = ?", (selected_pid,))

    curr_stage = proj["current_stage"]
    st.markdown(f"#### Project: `{selected_pid}` ({proj['project_name']}) | Current Stage: **{curr_stage}**")

    comp_pct = comp["disbursement_percentage"] if comp else 100.0
    pending_legal = legal["pending_cases"] if legal else 0
    doc_pct = doc["title_clearance_percentage"] if doc else 100.0
    app_delay = app["delay_days"] if app else 0
    rr_pct = rr["site_readiness_percentage"] if rr else 100.0

    stages_data = []
    for idx, stg in enumerate(LIFECYCLE_STAGES):
        if stg == "Legal Resolution":
            s_score = min(100.0, pending_legal * 6.5 + (20.0 if curr_stage == stg else 0.0))
            reason = f"{pending_legal} unresolved legal cases active in courts."
            evidence = f"Stay orders: {legal['stay_orders_count'] if legal else 0}, Total cases: {legal['total_cases'] if legal else 0}"
            action = "Establish dedicated legal resolution taskforce."
        elif stg == "Compensation":
            s_score = min(100.0, (100.0 - comp_pct) * 1.1)
            reason = f"Disbursement progress at {comp_pct:.1f}%, leaving pending beneficiaries."
            evidence = f"Amount sanctioned: ₹{comp['amount_sanctioned_cr'] if comp else 0} Cr"
            action = "Prioritize pending compensation bank transfers."
        elif stg == "Approval":
            s_score = min(100.0, app_delay * 0.9)
            reason = f"Statutory clearance pending for {app_delay} days."
            evidence = f"Clearance Status: {app['status'] if app else 'N/A'}"
            action = "Escalate to State Nodal Clearance Committee."
        elif stg == "Documentation":
            s_score = min(100.0, (100.0 - doc_pct) * 0.9)
            reason = f"Land title verification at {doc_pct:.1f}% title clearance."
            evidence = f"Records pending: {doc['records_pending'] if doc else 0}"
            action = "Deploy additional revenue inspectors."
        elif stg == "R&R":
            s_score = min(100.0, (100.0 - rr_pct) * 0.9)
            reason = f"Resettlement site readiness at {rr_pct:.1f}%."
            evidence = f"Families pending rehabilitation: {rr['families_pending'] if rr else 0}"
            action = "Accelerate R&R colony infrastructure development."
        else:
            s_score = round(max(10.0, min(60.0, 30.0 + (idx * 2))), 1)
            reason = f"Standard operational progress during {stg} stage."
            evidence = f"Stage Status: {'ACTIVE' if curr_stage == stg else 'NORMAL'}"
            action = f"Monitor milestone SLA for {stg}."

        level = "CRITICAL" if s_score > 80 else ("HIGH" if s_score > 60 else ("MEDIUM" if s_score > 30 else "LOW"))

        stages_data.append({
            "stage_name": stg,
            "risk_level": level,
            "risk_score": round(s_score, 1),
            "primary_reason": reason,
            "supporting_evidence": evidence,
            "recommended_action": action
        })

    sdf = pd.DataFrame(stages_data)

    fig = px.bar(
        sdf,
        x="risk_score",
        y="stage_name",
        orientation="h",
        color="risk_level",
        color_discrete_map={"CRITICAL": "#DC2626", "HIGH": "#EA580C", "MEDIUM": "#D97706", "LOW": "#16A34A"},
        labels={"risk_score": "Stage Risk Score (%)", "stage_name": "Acquisition Stage"}
    )
    fig.update_layout(height=420, margin=dict(t=10, b=10, l=10, r=10), yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Stage Diagnostic Cards")

    for s in stages_data:
        lvl = s["risk_level"]
        badge_cls = "badge-critical" if lvl == "CRITICAL" else ("badge-high" if lvl == "HIGH" else ("badge-medium" if lvl == "MEDIUM" else "badge-low"))
        st.markdown(f"""
        <div class="kpi-card">
            <div style="display:flex; justify-content:space-between;">
                <b>{s['stage_name']} Stage</b>
                <span class="{badge_cls}">{lvl} ({s['risk_score']}%)</span>
            </div>
            <div style="font-size:12px; margin-top:6px; color:#334155;">
                <b>Primary Reason:</b> {s['primary_reason']}<br/>
                <b>Evidence:</b> {s['supporting_evidence']}<br/>
                <b>Action Item:</b> {s['recommended_action']}
            </div>
        </div>
        """, unsafe_allow_html=True)
