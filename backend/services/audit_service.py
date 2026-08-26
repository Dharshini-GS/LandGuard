"""
Audit Logging Service for LANDGUARD AI.
Records security and user action events to SQLite audit_logs table.
"""

from datetime import datetime
import uuid
from typing import Dict, Any, Optional
from backend.database import execute_write
from utils.logger import get_logger

logger = get_logger("AuditService")

def log_action(user: Dict[str, Any], action: str, project_id: Optional[str] = None, details: str = ""):
    try:
        log_id = f"LOG-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        execute_write("""
        INSERT INTO audit_logs (log_id, user_id, username, role, scope_type, action, project_id, details, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            log_id,
            user.get("user_id", "SYSTEM"),
            user.get("username", "system"),
            user.get("role", "N/A"),
            user.get("scope_type", "N/A"),
            action,
            project_id or "",
            details,
            timestamp
        ))
    except Exception as e:
        logger.error(f"Failed to record audit log: {e}")
