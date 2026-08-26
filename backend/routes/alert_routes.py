"""
Alerts & Notifications Endpoints.
Connected to Centralized Alert Service.
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from datetime import datetime
from typing import Optional, List, Dict, Any

from backend.auth import get_current_user
from backend.permissions import build_scope_filter
from backend.database import execute_query_one, execute_write
from backend.services.alert_service import get_alerts
from backend.services.audit_service import log_action

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("")
def list_alerts_endpoint(
    status_filter: Optional[str] = Query(None, description="UNREAD or ACKNOWLEDGED"),
    severity_filter: Optional[str] = Query(None, description="CRITICAL or WARNING"),
    current_user: dict = Depends(get_current_user)
):
    return get_alerts(current_user, status_filter=status_filter, severity_filter=severity_filter)

@router.put("/{alert_id}/acknowledge")
def acknowledge_alert_endpoint(alert_id: str, current_user: dict = Depends(get_current_user)):
    # Check alert exists
    alert = execute_query_one("SELECT * FROM alerts WHERE alert_id = ?", (alert_id,))
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found.")

    # Scope verification
    scope_sql, params = build_scope_filter(current_user, table_prefix="p")
    auth_check = execute_query_one(
        f"SELECT p.project_id FROM projects p WHERE p.project_id = ? AND ({scope_sql})",
        tuple([alert["project_id"]] + params)
    )
    if not auth_check:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: Alert outside your scope.")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    execute_write("""
    UPDATE alerts
    SET status = 'ACKNOWLEDGED', acknowledged_by = ?, acknowledged_at = ?
    WHERE alert_id = ?
    """, (current_user["username"], timestamp, alert_id))

    log_action(current_user, "ACKNOWLEDGE_ALERT", project_id=alert["project_id"], details=f"Acknowledged alert {alert_id}")

    return {
        "alert_id": alert_id,
        "status": "ACKNOWLEDGED",
        "acknowledged_by": current_user["username"],
        "acknowledged_at": timestamp
    }
