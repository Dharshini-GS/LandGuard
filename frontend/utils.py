"""
Frontend Data API Client & Session Helper for LANDGUARD AI.
Directly interfaces with Backend Services and Database Repository for instant high-performance rendering.
"""

import streamlit as st
import sqlite3
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from backend.database import execute_query, execute_query_one, execute_write
from backend.permissions import build_scope_filter, verify_project_access
from backend.auth import verify_password
from backend.services.ml_service import ml_service_instance
from backend.services.audit_service import log_action

def get_current_session_user() -> Optional[Dict[str, Any]]:
    return st.session_state.get("user")

def login_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    user = execute_query_one("SELECT * FROM users WHERE username = ?", (username.strip(),))
    if not user:
        return None
    if not verify_password(password.strip(), user["password_hash"]):
        return None
    if user.get("status") != "ACTIVE":
        return None

    # Update last login
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    execute_write("UPDATE users SET last_login = ? WHERE user_id = ?", (ts, user["user_id"]))
    user_dict = dict(user)
    st.session_state["user"] = user_dict
    log_action(user_dict, "LOGIN", details="Logged in via Streamlit UI")
    return user_dict

def logout_user():
    user = st.session_state.get("user")
    if user:
        log_action(user, "LOGOUT", details="Logged out via Streamlit UI")
    st.session_state["user"] = None
    st.session_state["page"] = "Dashboard"

def get_scope_label(user: Dict[str, Any]) -> str:
    scope = user.get("scope_type", "NATIONAL")
    role = user.get("role", "ANALYST")
    if role == "ADMIN" or scope == "NATIONAL":
        return "NATIONAL SCOPE — INDIA"
    elif role == "STATE_OFFICER" or scope == "STATE":
        return f"STATE SCOPE — {user.get('state_name', 'ASSIGNED STATE')}"
    elif role == "DISTRICT_OFFICER" or scope == "DISTRICT":
        return f"DISTRICT SCOPE — {user.get('district_name', 'DISTRICT')}, {user.get('state_name', 'STATE')}"
    elif role == "PROJECT_MANAGER" or scope == "PROJECT":
        p_ids = user.get("assigned_project_ids", "")
        count = len([p for p in p_ids.split(",") if p.strip()])
        return f"PROJECT SCOPE — {count} ASSIGNED PROJECTS"
    return "NATIONAL SCOPE — INDIA"

def fetch_filtered_projects(
    user: Dict[str, Any],
    search: Optional[str] = None,
    state: Optional[str] = None,
    district: Optional[str] = None,
    project_type: Optional[str] = None,
    stage: Optional[str] = None,
    risk_cat: Optional[str] = None,
    limit: int = 200
) -> List[Dict[str, Any]]:
    scope_sql, params = build_scope_filter(user, table_prefix="p")
    conditions = [f"({scope_sql})"]
    query_params = list(params)

    if search:
        sterm = f"%{search.strip()}%"
        conditions.append("(p.project_id LIKE ? OR p.project_name LIKE ? OR p.state_name LIKE ? OR p.district_name LIKE ? OR p.project_type LIKE ?)")
        query_params.extend([sterm, sterm, sterm, sterm, sterm])

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

    if risk_cat:
        conditions.append("rh.risk_category = ?")
        query_params.append(risk_cat)

    where_str = " AND ".join(conditions)

    sql = f"""
    SELECT p.project_id, p.project_name, p.project_type, p.state_code, p.state_name, p.district_code, p.district_name,
           p.current_stage, p.status, p.land_area_acres, p.budget_inr_cr, p.start_date,
           rh.risk_category, rh.delay_probability, rh.risk_score, rh.expected_delay_days
    FROM projects p
    LEFT JOIN risk_history rh ON p.project_id = rh.project_id
    WHERE {where_str}
    ORDER BY rh.risk_score DESC
    LIMIT ?
    """
    query_params.append(limit)
    rows = execute_query(sql, tuple(query_params))

    res = []
    for r in rows:
        r_score = r["risk_score"] or 0.0
        p_score = round(r_score * 0.6 + (r["expected_delay_days"] or 0) * 0.4, 1)
        res.append({
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
            "priority_score": p_score,
            "status": r["status"]
        })
    return res
