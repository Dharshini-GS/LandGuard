"""
Projects Endpoint for LANDGUARD AI.
Supports scope-enforced search, filtering, sorting, pagination, and detail inspection.
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional, List, Dict, Any

from backend.auth import get_current_user
from backend.permissions import build_scope_filter, verify_project_access
from backend.database import execute_query, execute_query_one
from backend.services.ml_service import ml_service_instance
from backend.services.audit_service import log_action

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("")
def list_projects(
    search: Optional[str] = Query(None, description="Search by ID, name, state, district, type"),
    state: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    project_type: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    risk_category: Optional[str] = Query(None),
    sort_by: str = Query("risk_score", description="Field to sort by"),
    order: str = Query("desc", description="asc or desc"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    scope_sql, params = build_scope_filter(current_user, table_prefix="p")

    conditions = [f"({scope_sql})"]
    query_params = list(params)

    if search:
        s_term = f"%{search.strip()}%"
        conditions.append("""(
            p.project_id LIKE ? OR 
            p.project_name LIKE ? OR 
            p.state_name LIKE ? OR 
            p.district_name LIKE ? OR 
            p.project_type LIKE ?
        )""")
        query_params.extend([s_term, s_term, s_term, s_term, s_term])

    if state:
        conditions.append("p.state_code = ?")
        query_params.append(state)

    if district:
        conditions.append("p.district_code = ?")
        query_params.append(district)

    if project_type:
        conditions.append("p.project_type = ?")
        query_params.append(project_type)

    if stage:
        conditions.append("p.current_stage = ?")
        query_params.append(stage)

    if risk_category:
        conditions.append("rh.risk_category = ?")
        query_params.append(risk_category)

    where_clause = " AND ".join(conditions)

    # Valid sort fields
    valid_sorts = {
        "project_id": "p.project_id",
        "project_name": "p.project_name",
        "risk_score": "rh.risk_score",
        "delay_probability": "rh.delay_probability",
        "expected_delay_days": "rh.expected_delay_days",
        "start_date": "p.start_date"
    }
    sort_col = valid_sorts.get(sort_by, "rh.risk_score")
    sort_order = "DESC" if order.lower() == "desc" else "ASC"

    # Count Total
    count_sql = f"""
    SELECT COUNT(DISTINCT p.project_id) AS total
    FROM projects p
    LEFT JOIN risk_history rh ON p.project_id = rh.project_id
    WHERE {where_clause}
    """
    total_res = execute_query_one(count_sql, tuple(query_params))
    total_count = total_res["total"] if total_res else 0

    # Fetch Page Data
    offset = (page - 1) * limit
    sql = f"""
    SELECT 
        p.project_id, p.project_name, p.project_type, p.state_code, p.state_name, p.district_code, p.district_name,
        p.current_stage, p.status, p.start_date, p.target_completion_date,
        rh.risk_category, rh.delay_probability, rh.risk_score, rh.expected_delay_days
    FROM projects p
    LEFT JOIN risk_history rh ON p.project_id = rh.project_id
    WHERE {where_clause}
    ORDER BY {sort_col} {sort_order}
    LIMIT ? OFFSET ?
    """
    page_params = query_params + [limit, offset]
    rows = execute_query(sql, tuple(page_params))

    # Format list output
    items = []
    for r in rows:
        r_score = r["risk_score"] or 0.0
        # Multi-criteria priority score = risk_score * 0.6 + expected_delay * 0.4
        priority_score = round(r_score * 0.6 + (r["expected_delay_days"] or 0) * 0.4, 1)
        items.append({
            "project_id": r["project_id"],
            "project_name": r["project_name"],
            "project_type": r["project_type"],
            "state_code": r["state_code"],
            "state_name": r["state_name"],
            "district_code": r["district_code"],
            "district_name": r["district_name"],
            "current_stage": r["current_stage"],
            "risk_category": r["risk_category"] or "LOW",
            "delay_probability": round(r["delay_probability"] or 0.0, 4),
            "risk_score": r_score,
            "expected_delay_days": r["expected_delay_days"] or 0,
            "priority_score": priority_score,
            "status": r["status"]
        })

    return {
        "total": total_count,
        "page": page,
        "limit": limit,
        "pages": (total_count + limit - 1) // limit if total_count > 0 else 1,
        "data": items
    }

@router.get("/{project_id}")
def get_project_detail(project_id: str, current_user: dict = Depends(get_current_user)):
    # Security requirement: Enforce authorization scope (raises 403 if out of scope)
    verify_project_access(current_user, project_id)

    # Fetch complete project detail
    proj = execute_query_one("SELECT * FROM projects WHERE project_id = ?", (project_id,))
    comp = execute_query_one("SELECT * FROM compensation WHERE project_id = ?", (project_id,))
    legal = execute_query_one("SELECT * FROM legal_disputes WHERE project_id = ?", (project_id,))
    approvals = execute_query("SELECT * FROM approvals WHERE project_id = ?", (project_id,))
    doc = execute_query_one("SELECT * FROM documentation WHERE project_id = ?", (project_id,))
    rr = execute_query_one("SELECT * FROM rehabilitation_rr WHERE project_id = ?", (project_id,))
    stk = execute_query_one("SELECT * FROM stakeholders WHERE project_id = ?", (project_id,))
    adm = execute_query_one("SELECT * FROM administrative_performance WHERE project_id = ?", (project_id,))
    geo = execute_query_one("SELECT * FROM project_geospatial WHERE project_id = ?", (project_id,))

    # Real ML prediction
    risk_info = ml_service_instance.predict_risk(project_id)

    log_action(current_user, "VIEW_PROJECT", project_id=project_id, details=f"Viewed project detail {project_id}")

    return {
        "project_id": proj["project_id"],
        "project_name": proj["project_name"],
        "project_type": proj["project_type"],
        "state_code": proj["state_code"],
        "state_name": proj["state_name"],
        "district_code": proj["district_code"],
        "district_name": proj["district_name"],
        "land_area_acres": proj["land_area_acres"],
        "affected_families": proj["affected_families"],
        "landowners_count": proj["landowners_count"],
        "budget_inr_cr": proj["budget_inr_cr"],
        "current_stage": proj["current_stage"],
        "start_date": proj["start_date"],
        "target_completion_date": proj["target_completion_date"],
        "status": proj["status"],
        "compensation": dict(comp) if comp else {},
        "legal_disputes": dict(legal) if legal else {},
        "approvals": [dict(a) for a in approvals],
        "documentation": dict(doc) if doc else {},
        "rehabilitation": dict(rr) if rr else {},
        "stakeholders": dict(stk) if stk else {},
        "administrative": dict(adm) if adm else {},
        "geospatial": dict(geo) if geo else {},
        "risk_info": risk_info
    }
