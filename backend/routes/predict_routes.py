"""
Prediction & What-If Simulation Endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
import uuid
import json
from datetime import datetime

from backend.auth import get_current_user
from backend.permissions import verify_project_access
from backend.schemas import SimulationRequest, SimulationResponse
from backend.services.ml_service import ml_service_instance
from backend.database import execute_write
from backend.services.audit_service import log_action

router = APIRouter(tags=["Predict & Simulate"])

@router.post("/predict")
def predict_project(project_id: str, current_user: dict = Depends(get_current_user)):
    verify_project_access(current_user, project_id)
    return ml_service_instance.predict_risk(project_id)

@router.post("/simulate", response_model=SimulationResponse)
def run_simulation(req: SimulationRequest, current_user: dict = Depends(get_current_user)):
    verify_project_access(current_user, req.project_id)

    mods = {
        "compensation_completion_pct": req.compensation_completion_pct,
        "pending_legal_cases": req.pending_legal_cases,
        "approval_delay_days": req.approval_delay_days,
        "documentation_completion_pct": req.documentation_completion_pct,
        "rr_completion_pct": req.rr_completion_pct,
        "stakeholder_response_idx": req.stakeholder_response_idx
    }

    res = ml_service_instance.simulate_what_if(req.project_id, mods)

    # Record simulation in SQLite operational table
    sim_id = f"SIM-{uuid.uuid4().hex[:8].upper()}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    execute_write("""
    INSERT INTO simulations (sim_id, project_id, user_id, parameters_json, initial_risk_score, simulated_risk_score, risk_reduction, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        sim_id,
        req.project_id,
        current_user["user_id"],
        json.dumps(mods),
        res["initial_risk_score"],
        res["simulated_risk_score"],
        res["risk_reduction"],
        timestamp
    ))

    log_action(current_user, "RUN_SIMULATION", project_id=req.project_id, details=f"Ran what-if simulation: initial={res['initial_risk_score']}%, sim={res['simulated_risk_score']}%, delta={res['risk_reduction']}%")

    return SimulationResponse(
        project_id=req.project_id,
        initial_risk_score=res["initial_risk_score"],
        initial_risk_category=res["initial_risk_category"],
        simulated_risk_score=res["simulated_risk_score"],
        simulated_risk_category=res["simulated_risk_category"],
        risk_reduction=res["risk_reduction"],
        simulated_expected_delay_days=res["simulated_expected_delay_days"],
        disclaimer=res["disclaimer"]
    )
