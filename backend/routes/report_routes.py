"""
PDF Report Generation Endpoint for LANDGUARD AI.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from backend.auth import get_current_user
from backend.permissions import verify_project_access
from backend.services.pdf_service import generate_project_pdf_report
from backend.services.audit_service import log_action

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/project/{project_id}")
def download_project_report(project_id: str, current_user: dict = Depends(get_current_user)):
    # Scope check
    verify_project_access(current_user, project_id)

    # Generate PDF
    filepath = generate_project_pdf_report(project_id)

    log_action(current_user, "EXPORT_REPORT", project_id=project_id, details=f"Generated PDF risk report for {project_id}")

    return FileResponse(
        path=str(filepath),
        filename=f"LANDGUARD_Risk_Report_{project_id}.pdf",
        media_type="application/pdf"
    )
