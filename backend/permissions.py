"""
Scope & Authorization Enforcement Engine for VISTRA.
Enforces geographic and project-level RBAC restrictions at the database/query layer.
Never relies on frontend filtering. Unauthorized access yields HTTP 403.
"""

from fastapi import HTTPException, status
from typing import Dict, Any, Tuple, List
from backend.database import execute_query_one

def build_scope_filter(user: Dict[str, Any], table_prefix: str = "p") -> Tuple[str, List[Any]]:
    """
    Returns SQL WHERE fragment and parameters based on user's role and scope.
    """
    role = user.get("role")
    scope = user.get("scope_type")
    p_prefix = f"{table_prefix}." if table_prefix else ""

    if role == "ADMIN" or scope == "NATIONAL":
        return "1=1", []

    if role == "STATE_OFFICER" or scope == "STATE":
        st_code = user.get("state_code", "")
        return f"{p_prefix}state_code = ?", [st_code]

    if role == "DISTRICT_OFFICER" or scope == "DISTRICT":
        st_code = user.get("state_code", "")
        dist_code = user.get("district_code", "")
        return f"{p_prefix}state_code = ? AND {p_prefix}district_code = ?", [st_code, dist_code]

    if role == "PROJECT_MANAGER" or scope == "PROJECT":
        assigned_str = user.get("assigned_project_ids", "")
        if not assigned_str:
            return "1=0", []  # No assigned projects
        p_ids = [pid.strip() for pid in assigned_str.split(",") if pid.strip()]
        if not p_ids:
            return "1=0", []
        placeholders = ", ".join(["?"] * len(p_ids))
        return f"{p_prefix}project_id IN ({placeholders})", p_ids

    # Fallback to analyst scope checking
    if scope == "STATE":
        return f"{p_prefix}state_code = ?", [user.get("state_code", "")]
    elif scope == "DISTRICT":
        return f"{p_prefix}state_code = ? AND {p_prefix}district_code = ?", [user.get("state_code", ""), user.get("district_code", "")]
    elif scope == "PROJECT":
        assigned_str = user.get("assigned_project_ids", "")
        p_ids = [pid.strip() for pid in assigned_str.split(",") if pid.strip()]
        if not p_ids:
            return "1=0", []
        placeholders = ", ".join(["?"] * len(p_ids))
        return f"{p_prefix}project_id IN ({placeholders})", p_ids

    return "1=1", []

def verify_project_access(user: Dict[str, Any], project_id: str) -> Dict[str, Any]:
    """
    Verifies that the requested project_id exists AND is authorized for the current user.
    Returns project record if allowed, or raises HTTP 403 Forbidden.
    """
    scope_sql, params = build_scope_filter(user, table_prefix="p")
    query = f"""
    SELECT p.project_id, p.project_name, p.state_code, p.district_code, p.project_type
    FROM projects p
    WHERE p.project_id = ? AND ({scope_sql})
    """
    full_params = [project_id] + params
    project = execute_query_one(query, tuple(full_params))

    if not project:
        # Check if project exists at all to prevent leaking existence info or 403 forbidden
        proj_exists = execute_query_one("SELECT project_id FROM projects WHERE project_id = ?", (project_id,))
        if proj_exists:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Project outside your authorized scope."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found."
            )

    return project
