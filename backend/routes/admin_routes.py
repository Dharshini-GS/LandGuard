"""
Admin, User Management, Model Management, & Audit Logs Endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List, Dict, Any
import json
import uuid
from datetime import datetime

from backend.auth import get_current_user, hash_password
from backend.database import execute_query, execute_query_one, execute_write
from backend.schemas import UserCreateRequest, UserUpdateRequest
from backend.services.audit_service import log_action
from scripts.update_model import update_model
from utils.config import MODEL_METADATA_PATH, DATABASE_PATH

router = APIRouter(prefix="/admin", tags=["Administration"])

def verify_admin(user: dict):
    if user.get("role") != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required.")

@router.get("/audit-logs")
def get_audit_logs(limit: int = 100, current_user: dict = Depends(get_current_user)):
    verify_admin(current_user)
    logs = execute_query("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?", (limit,))
    return {"count": len(logs), "logs": [dict(l) for l in logs]}

@router.get("/users")
def get_users(current_user: dict = Depends(get_current_user)):
    verify_admin(current_user)
    users = execute_query("SELECT user_id, username, full_name, role, scope_type, state_code, state_name, district_code, district_name, assigned_project_ids, status, created_at, last_login FROM users ORDER BY created_at DESC")
    return {"count": len(users), "users": [dict(u) for u in users]}

@router.post("/users")
def create_user(req: UserCreateRequest, current_user: dict = Depends(get_current_user)):
    verify_admin(current_user)

    existing = execute_query_one("SELECT user_id FROM users WHERE username = ?", (req.username.strip(),))
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists.")

    u_id = f"USR-{uuid.uuid4().hex[:8].upper()}"
    p_hash = hash_password(req.password.strip())
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    execute_write("""
    INSERT INTO users (user_id, username, password_hash, full_name, role, scope_type, state_code, state_name, district_code, district_name, assigned_project_ids, status, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?)
    """, (
        u_id, req.username.strip(), p_hash, req.full_name.strip(), req.role, req.scope_type,
        req.state_code or "", req.state_name or "", req.district_code or "", req.district_name or "",
        req.assigned_project_ids or "", timestamp
    ))

    log_action(current_user, "CREATE_USER", details=f"Created user {req.username} ({req.role})")

    return {"user_id": u_id, "username": req.username, "status": "ACTIVE"}

@router.get("/model/status")
def get_model_status(current_user: dict = Depends(get_current_user)):
    p_cnt = execute_query_one("SELECT COUNT(*) AS cnt FROM projects")["cnt"]
    u_cnt = execute_query_one("SELECT COUNT(*) AS cnt FROM users")["cnt"]
    a_cnt = execute_query_one("SELECT COUNT(*) AS cnt FROM alerts WHERE status = 'UNREAD'")["cnt"]

    meta = {}
    if MODEL_METADATA_PATH.exists():
        with open(MODEL_METADATA_PATH, "r", encoding="utf-8") as f:
            meta = json.load(f)

    return {
        "database_status": "HEALTHY",
        "database_path": str(DATABASE_PATH),
        "total_projects": p_cnt,
        "total_users": u_cnt,
        "active_unread_alerts": a_cnt,
        "model_version": meta.get("model_version", "v1.0.0"),
        "trained_date": meta.get("trained_date", "N/A"),
        "dataset_size": meta.get("dataset_size", p_cnt)
    }

@router.get("/model/metrics")
def get_model_metrics(current_user: dict = Depends(get_current_user)):
    if not MODEL_METADATA_PATH.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model metadata not found.")

    with open(MODEL_METADATA_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    return meta

@router.post("/model/retrain")
def trigger_retrain(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") not in ["ADMIN", "ANALYST"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied.")

    update_model()
    log_action(current_user, "UPDATE_MODEL", details="Triggered model retraining pipeline")
    return {"message": "Model retrain completed successfully."}
