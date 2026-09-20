"""
GIS Map Endpoint for VISTRA.
Returns geospatial coordinates and risk metadata strictly constrained to the user's scope.
"""

from fastapi import APIRouter, Depends, Query

from backend.auth import get_current_user
from backend.permissions import build_scope_filter
from backend.database import execute_query
from backend.services.audit_service import log_action

router = APIRouter(prefix="/map", tags=["GIS Map"])

@router.get("/projects")
def get_map_projects(
    risk_category: str = Query(None),
    state: str = Query(None),
    district: str = Query(None),
    current_user: dict = Depends(get_current_user)
):
    scope_sql, params = build_scope_filter(current_user, table_prefix="p")

    conditions = [f"({scope_sql})"]
    query_params = list(params)

    if risk_category:
        conditions.append("rh.risk_category = ?")
        query_params.append(risk_category.upper())

    if state:
        conditions.append("p.state_code = ?")
        query_params.append(state)

    if district:
        conditions.append("p.district_code = ?")
        query_params.append(district)

    where_clause = " AND ".join(conditions)

    sql = f"""
    SELECT 
        p.project_id, p.project_name, p.project_type, p.state_code, p.state_name, p.district_code, p.district_name,
        p.current_stage, g.latitude, g.longitude,
        rh.risk_category, rh.delay_probability, rh.risk_score, rh.expected_delay_days
    FROM projects p
    JOIN project_geospatial g ON p.project_id = g.project_id
    LEFT JOIN risk_history rh ON p.project_id = rh.project_id
    WHERE {where_clause}
    LIMIT 500
    """

    rows = execute_query(sql, tuple(query_params))

    log_action(current_user, "VIEW_MAP", details=f"Viewed GIS map ({len(rows)} projects displayed)")

    markers = []
    for r in rows:
        markers.append({
            "project_id": r["project_id"],
            "project_name": r["project_name"],
            "project_type": r["project_type"],
            "state_code": r["state_code"],
            "state_name": r["state_name"],
            "district_code": r["district_code"],
            "district_name": r["district_name"],
            "current_stage": r["current_stage"],
            "latitude": r["latitude"],
            "longitude": r["longitude"],
            "risk_category": r["risk_category"] or "LOW",
            "delay_probability": round(r["delay_probability"] or 0.0, 4),
            "risk_score": r["risk_score"] or 0.0,
            "expected_delay_days": r["expected_delay_days"] or 0,
            "disclaimer": "Synthetic Prototype Project Location"
        })

    return {
        "count": len(markers),
        "scope": current_user.get("scope_type"),
        "data": markers
    }
