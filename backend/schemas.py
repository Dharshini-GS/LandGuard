"""
Pydantic Schemas for VISTRA FastAPI Endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Authentication
class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    user_id: str
    username: str
    full_name: str
    role: str
    scope_type: str
    state_code: Optional[str] = ""
    state_name: Optional[str] = ""
    district_code: Optional[str] = ""
    district_name: Optional[str] = ""
    assigned_project_ids: Optional[str] = ""
    status: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Projects
class ProjectListItem(BaseModel):
    project_id: str
    project_name: str
    project_type: str
    state_code: str
    state_name: str
    district_code: str
    district_name: str
    current_stage: str
    risk_category: str
    delay_probability: float
    expected_delay_days: int
    priority_score: float
    status: str

class ProjectDetail(BaseModel):
    project_id: str
    project_name: str
    project_type: str
    state_code: str
    state_name: str
    district_code: str
    district_name: str
    land_area_acres: float
    affected_families: int
    landowners_count: int
    budget_inr_cr: float
    current_stage: str
    start_date: str
    target_completion_date: str
    status: str
    compensation: Dict[str, Any]
    legal_disputes: Dict[str, Any]
    approvals: List[Dict[str, Any]]
    documentation: Dict[str, Any]
    rehabilitation: Dict[str, Any]
    stakeholders: Dict[str, Any]
    administrative: Dict[str, Any]
    geospatial: Dict[str, Any]
    risk_info: Dict[str, Any]

# Risk & SHAP
class RiskAssessment(BaseModel):
    project_id: str
    delay_probability: float
    risk_score: float
    risk_category: str
    expected_delay_days: int
    highest_risk_stage: str
    model_version: str

class StageRiskItem(BaseModel):
    stage_name: str
    risk_level: str
    risk_score: float
    primary_reason: str
    supporting_evidence: str
    recommended_action: str

class SHAPFactor(BaseModel):
    feature_name: str
    human_label: str
    shap_value: float
    feature_value: Any
    impact_direction: str
    explanation: str

class SHAPExplanation(BaseModel):
    project_id: str
    delay_probability: float
    risk_category: str
    base_value: float
    top_contributors: List[SHAPFactor]
    summary_human: str

# Simulation
class SimulationRequest(BaseModel):
    project_id: str
    compensation_completion_pct: Optional[float] = None
    pending_legal_cases: Optional[int] = None
    approval_delay_days: Optional[int] = None
    documentation_completion_pct: Optional[float] = None
    rr_completion_pct: Optional[float] = None
    stakeholder_response_idx: Optional[float] = None

class SimulationResponse(BaseModel):
    project_id: str
    initial_risk_score: float
    initial_risk_category: str
    simulated_risk_score: float
    simulated_risk_category: str
    risk_reduction: float
    simulated_expected_delay_days: int
    disclaimer: str

# Alerts
class AlertItem(BaseModel):
    alert_id: str
    project_id: str
    alert_type: str
    severity: str
    title: str
    message: str
    status: str
    created_at: str
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[str] = None

# AI Assistant
class AIQueryRequest(BaseModel):
    query: str

class AIQueryResponse(BaseModel):
    answer: str
    related_projects: List[Dict[str, Any]]
    scope_applied: str

# User Management Admin
class UserCreateRequest(BaseModel):
    username: str
    password: str
    full_name: str
    role: str
    scope_type: str
    state_code: Optional[str] = ""
    state_name: Optional[str] = ""
    district_code: Optional[str] = ""
    district_name: Optional[str] = ""
    assigned_project_ids: Optional[str] = ""

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    scope_type: Optional[str] = None
    state_code: Optional[str] = None
    district_code: Optional[str] = None
    assigned_project_ids: Optional[str] = None
    status: Optional[str] = None
