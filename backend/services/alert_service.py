"""
Centralized Alert Service for LANDGUARD AI.
Evaluates authoritative project data & risk history, generates alerts, enforces scope, and synchronizes counts.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from backend.database import execute_query, execute_query_one, execute_write
from backend.permissions import build_scope_filter

def sync_and_generate_alerts():
    """
    Evaluates projects and risk history to ensure authoritative alerts exist in the database.
    Prevents duplicates while ensuring all critical/high risk projects trigger alerts.
    """
    # 1. Critical and High Risk Projects
    sql_risk = """
    SELECT r.project_id, r.risk_category, r.risk_score, r.expected_delay_days, p.project_name, p.state_name
    FROM risk_history r
    JOIN projects p ON r.project_id = p.project_id
    WHERE r.risk_category IN ('CRITICAL', 'HIGH')
    """
    risk_rows = execute_query(sql_risk)

    for r in risk_rows:
        p_id = r["project_id"]
        cat = r["risk_category"]
        score = r["risk_score"]
        delay = r["expected_delay_days"]
        p_name = r["project_name"]

        # Check existing alert
        existing = execute_query_one(
            "SELECT alert_id FROM alerts WHERE project_id = ? AND alert_type = ?",
            (p_id, "CRITICAL_RISK" if cat == "CRITICAL" else "HIGH_RISK")
        )
        if not existing:
            alert_id = f"ALT-{cat[:3]}-{p_id}"
            sev = "CRITICAL" if cat == "CRITICAL" else "WARNING"
            alert_type = "CRITICAL_RISK" if cat == "CRITICAL" else "HIGH_RISK"
            title = f"{cat} Risk Alert: {p_id}"
            msg = f"Project '{p_name}' has reached a risk score of {score:.1f}% ({cat}) with an expected delay of {delay} days."
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            execute_write("""
            INSERT OR IGNORE INTO alerts (alert_id, project_id, alert_type, severity, title, message, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'UNREAD', ?)
            """, (alert_id, p_id, alert_type, sev, title, msg, ts))

def get_alerts(
    user: dict,
    status_filter: Optional[str] = None,
    severity_filter: Optional[str] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Fetches synchronized alerts for the user's scope.
    """
    sync_and_generate_alerts()

    scope_sql, params = build_scope_filter(user, table_prefix="p")
    conditions = [f"({scope_sql})"]
    query_params = list(params)

    if status_filter and status_filter != "ALL":
        conditions.append("a.status = ?")
        query_params.append(status_filter.upper())

    if severity_filter and severity_filter != "ALL":
        conditions.append("a.severity = ?")
        query_params.append(severity_filter.upper())

    where_clause = " AND ".join(conditions)

    sql = f"""
    SELECT a.alert_id, a.project_id, a.alert_type, a.severity, a.title, a.message, a.status, a.created_at,
           a.acknowledged_by, a.acknowledged_at,
           p.project_name, p.state_name, p.district_name, p.current_stage,
           rh.risk_score, rh.expected_delay_days, rh.risk_category
    FROM alerts a
    JOIN projects p ON a.project_id = p.project_id
    LEFT JOIN risk_history rh ON p.project_id = rh.project_id
    WHERE {where_clause}
    ORDER BY a.created_at DESC
    LIMIT {limit}
    """

    rows = execute_query(sql, tuple(query_params))

    # Calculate summary metrics strictly within scope
    summary_sql = f"""
    SELECT 
        COUNT(*) AS total_alerts,
        SUM(CASE WHEN a.status = 'UNREAD' THEN 1 ELSE 0 END) AS unread_cnt,
        SUM(CASE WHEN a.severity = 'CRITICAL' THEN 1 ELSE 0 END) AS critical_cnt,
        SUM(CASE WHEN a.severity = 'WARNING' THEN 1 ELSE 0 END) AS warning_cnt,
        SUM(CASE WHEN a.status = 'ACKNOWLEDGED' THEN 1 ELSE 0 END) AS ack_cnt
    FROM alerts a
    JOIN projects p ON a.project_id = p.project_id
    WHERE {scope_sql}
    """
    s_res = execute_query_one(summary_sql, tuple(params)) or {}

    return {
        "total_alerts": s_res.get("total_alerts", 0) or 0,
        "unread_count": s_res.get("unread_cnt", 0) or 0,
        "critical_count": s_res.get("critical_cnt", 0) or 0,
        "warning_count": s_res.get("warning_cnt", 0) or 0,
        "acknowledged_count": s_res.get("ack_cnt", 0) or 0,
        "alerts": [dict(r) for r in rows] if rows else []
    }
