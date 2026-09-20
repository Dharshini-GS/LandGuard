"""
Scope-Aware AI Assistant Endpoint for VISTRA.
Provides local deterministic risk analytics queries respecting user scope bounds.
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any, List

from backend.auth import get_current_user
from backend.permissions import build_scope_filter
from backend.database import execute_query
from backend.schemas import AIQueryRequest, AIQueryResponse
from backend.services.audit_service import log_action

router = APIRouter(prefix="/ai-assistant", tags=["AI Assistant"])

@router.post("/query", response_model=AIQueryResponse)
def query_ai_assistant(req: AIQueryRequest, current_user: dict = Depends(get_current_user)):
    query_text = req.query.strip().lower()
    scope_type = current_user.get("scope_type", "NATIONAL")
    role = current_user.get("role", "ANALYST")

    scope_sql, params = build_scope_filter(current_user, table_prefix="p")

    # Scope indication string
    if scope_type == "STATE":
        scope_label = f"STATE SCOPE — {current_user.get('state_name', 'STATE')}"
    elif scope_type == "DISTRICT":
        scope_label = f"DISTRICT SCOPE — {current_user.get('district_name', 'DISTRICT')}, {current_user.get('state_name', 'STATE')}"
    elif scope_type == "PROJECT":
        scope_label = f"PROJECT SCOPE — {current_user.get('assigned_project_ids', 'ASSIGNED')}"
    else:
        scope_label = "NATIONAL SCOPE — INDIA"

    # Fetch top critical/high risk projects within scope
    sql = f"""
    SELECT p.project_id, p.project_name, p.state_name, p.district_name, p.current_stage, p.project_type,
           rh.risk_category, rh.risk_score, rh.expected_delay_days, rh.delay_probability
    FROM projects p
    LEFT JOIN risk_history rh ON p.project_id = rh.project_id
    WHERE ({scope_sql})
    ORDER BY rh.risk_score DESC
    LIMIT 5
    """
    top_projects = execute_query(sql, tuple(params))

    # Formulate answer
    if not top_projects:
        answer = f"No projects found within your authorized scope ({scope_label})."
        related = []
    elif "critical" in query_text or "immediate" in query_text or "attention" in query_text:
        crit_list = [p for p in top_projects if p["risk_category"] == "CRITICAL"]
        cnt = len(crit_list)
        if cnt > 0:
            names = ", ".join([f"<b>{p['project_id']}</b> ({p['project_name']} - {p['risk_score']}%)" for p in crit_list[:3]])
            answer = f"Within {scope_label}, there are <b>{cnt} CRITICAL-risk projects</b> requiring immediate intervention: {names}. Primary bottlenecks center around legal stay orders and compensation disbursement delays."
        else:
            answer = f"Within {scope_label}, no project is currently in the CRITICAL category. The highest risk project is <b>{top_projects[0]['project_id']}</b> at {top_projects[0]['risk_score']}% risk."
        related = [dict(p) for p in top_projects]

    elif "highest risk" in query_text or "worst" in query_text or "top" in query_text:
        p1 = top_projects[0]
        answer = f"The highest-risk project under {scope_label} is <b>{p1['project_id']}</b> ({p1['project_name']}) in {p1['district_name']}, {p1['state_name']}. It has a predicted delay probability of <b>{p1['delay_probability']*100:.1f}%</b> ({p1['risk_category']}) with an estimated completion delay of <b>{p1['expected_delay_days']} days</b>."
        related = [dict(p) for p in top_projects]

    elif "action" in query_text or "recommend" in query_text:
        p1 = top_projects[0]
        answer = f"For top risk projects under {scope_label} (such as <b>{p1['project_id']}</b>), key recommended actions are: 1) Accelerate direct benefit compensation payments, 2) Fast-track pending district court stay order resolutions, and 3) Escalate clearance applications to nodal officers."
        related = [dict(p) for p in top_projects]

    else:
        # General scope summary
        answer = f"Analyzed records for {scope_label}. Found {len(top_projects)} high-priority projects. Top project <b>{top_projects[0]['project_id']}</b> ({top_projects[0]['project_name']}) stands at {top_projects[0]['risk_score']}% risk ({top_projects[0]['risk_category']})."
        related = [dict(p) for p in top_projects]

    log_action(current_user, "AI_ASSISTANT_QUERY", details=f"Query: '{req.query}' | Scope: {scope_label}")

    return AIQueryResponse(
        answer=answer,
        related_projects=related,
        scope_applied=scope_label
    )
