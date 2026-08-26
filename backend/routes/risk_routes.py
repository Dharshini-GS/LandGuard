"""
Risk Assessment, Stage-wise Breakdown, and SHAP Explanation Endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from backend.auth import get_current_user
from backend.permissions import verify_project_access
from backend.services.ml_service import ml_service_instance
from backend.database import execute_query_one, execute_query
from utils.geo_data import LIFECYCLE_STAGES
from backend.services.audit_service import log_action

router = APIRouter(prefix="/projects", tags=["Risk & Intelligence"])

@router.get("/{project_id}/risk")
def get_project_risk(project_id: str, current_user: dict = Depends(get_current_user)):
    verify_project_access(current_user, project_id)
    risk_info = ml_service_instance.predict_risk(project_id)
    log_action(current_user, "VIEW_RISK", project_id=project_id, details="Viewed project risk prediction")
    return risk_info

@router.get("/{project_id}/stage-risk")
def get_stage_risk(project_id: str, current_user: dict = Depends(get_current_user)):
    verify_project_access(current_user, project_id)
    proj = execute_query_one("SELECT * FROM projects WHERE project_id = ?", (project_id,))
    comp = execute_query_one("SELECT * FROM compensation WHERE project_id = ?", (project_id,))
    legal = execute_query_one("SELECT * FROM legal_disputes WHERE project_id = ?", (project_id,))
    doc = execute_query_one("SELECT * FROM documentation WHERE project_id = ?", (project_id,))
    app = execute_query_one("SELECT * FROM approvals WHERE project_id = ?", (project_id,))
    rr = execute_query_one("SELECT * FROM rehabilitation_rr WHERE project_id = ?", (project_id,))

    curr_stage = proj["current_stage"]
    stages_data = []

    # Map features to each stage
    comp_pct = comp["disbursement_percentage"] if comp else 100.0
    pending_legal = legal["pending_cases"] if legal else 0
    doc_pct = doc["title_clearance_percentage"] if doc else 100.0
    app_delay = app["delay_days"] if app else 0
    rr_pct = rr["site_readiness_percentage"] if rr else 100.0

    for idx, stg in enumerate(LIFECYCLE_STAGES):
        # Stage risk score calculation
        if stg == "Legal Resolution":
            s_score = min(100.0, pending_legal * 6.5 + (20.0 if curr_stage == stg else 0.0))
            reason = f"{pending_legal} unresolved legal cases active in district/high courts."
            evidence = f"Stay orders: {legal['stay_orders_count'] if legal else 0}, Total cases: {legal['total_cases'] if legal else 0}"
            action = "Establish dedicated legal resolution taskforce and fast-track court hearings."
        elif stg == "Compensation":
            s_score = min(100.0, (100.0 - comp_pct) * 1.1)
            reason = f"Disbursement progress at {comp_pct:.1f}%, leaving {comp['beneficiaries_pending'] if comp else 0} pending beneficiaries."
            evidence = f"Amount sanctioned: ₹{comp['amount_sanctioned_cr'] if comp else 0} Cr, Disbursed: ₹{comp['amount_disbursed_cr'] if comp else 0} Cr"
            action = "Prioritize pending compensation bank transfers and set up grievance helpdesk."
        elif stg == "Approval":
            s_score = min(100.0, app_delay * 0.9)
            reason = f"Statutory clearance pending for {app_delay} days past standard SLA."
            evidence = f"Clearance Type: {app['approval_type'] if app else 'N/A'}, Status: {app['status'] if app else 'N/A'}"
            action = "Escalate clearance file to State Nodal Clearance Committee."
        elif stg == "Documentation":
            s_score = min(100.0, (100.0 - doc_pct) * 0.9)
            reason = f"Land title verification at {doc_pct:.1f}% title clearance."
            evidence = f"Records pending: {doc['records_pending'] if doc else 0} out of {doc['total_records'] if doc else 0}"
            action = "Deploy additional revenue inspectors for field record verification."
        elif stg == "R&R":
            s_score = min(100.0, (100.0 - rr_pct) * 0.9)
            reason = f"Resettlement site readiness at {rr_pct:.1f}%."
            evidence = f"Families pending rehabilitation: {rr['families_pending'] if rr else 0}"
            action = "Accelerate R&R colony infrastructure development and house allotment."
        else:
            s_score = round(max(10.0, min(60.0, 30.0 + (idx * 2) - (10 if curr_stage != stg else 0))), 1)
            reason = f"Standard operational progress during {stg} stage."
            evidence = f"Current Stage Status: {'ACTIVE' if curr_stage == stg else 'COMPLETED/PENDING'}"
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

    return {
        "project_id": project_id,
        "current_stage": curr_stage,
        "stages": stages_data
    }

@router.get("/{project_id}/explanation")
def get_shap_explanation(project_id: str, current_user: dict = Depends(get_current_user)):
    verify_project_access(current_user, project_id)
    shap_info = ml_service_instance.explain_shap(project_id)
    log_action(current_user, "VIEW_EXPLANATION", project_id=project_id, details="Viewed SHAP explainable AI attribution")
    return shap_info
