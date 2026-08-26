"""
Comprehensive Automated Acceptance Test Suite for LANDGUARD AI (SIH26017 Prototype).
Tests all 16 prompt acceptance criteria using pytest and FastAPI TestClient.
"""

import pytest
import sqlite3
import json
from pathlib import Path
from fastapi.testclient import TestClient

import sys
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.main import app
from backend.database import execute_query_one, execute_query, execute_write
from backend.services.ml_service import ml_service_instance
from utils.config import DATABASE_PATH
from utils.geo_data import GEO_REFERENCE

client = TestClient(app)

# Helper function to obtain auth token
def get_auth_token(username, password):
    resp = client.post("/login", json={"username": username, "password": password})
    assert resp.status_code == 200, f"Login failed for {username}: {resp.json()}"
    return resp.json()["access_token"]

def get_auth_header(username, password):
    token = get_auth_token(username, password)
    return {"Authorization": f"Bearer {token}"}

# TEST 1: ADMIN Login & National Scope
def test_01_admin_national_scope():
    headers = get_auth_header("admin", "admin123")
    resp = client.get("/me", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["role"] == "ADMIN"
    assert data["scope_type"] == "NATIONAL"

# TEST 2: STATE OFFICER Login (Tamil Nadu)
def test_02_state_officer_scope():
    headers = get_auth_header("state_tn", "state123")
    resp = client.get("/projects", headers=headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    # All projects must belong to TN
    for p in data:
        assert p["state_code"] == "TN"

# TEST 3: BACKEND AUTHORIZATION ENFORCEMENT (HTTP 403)
def test_03_authorization_403_enforcement():
    headers = get_auth_header("state_tn", "state123")
    # Find a non-TN project ID (e.g. Maharashtra project)
    non_tn_proj = execute_query_one("SELECT project_id FROM projects WHERE state_code != 'TN' LIMIT 1")
    assert non_tn_proj is not None
    target_pid = non_tn_proj["project_id"]

    # Attempt direct request
    resp = client.get(f"/projects/{target_pid}", headers=headers)
    assert resp.status_code == 403, f"Expected 403 Forbidden, got {resp.status_code}"
    assert "Access denied" in resp.json()["detail"]

# TEST 4: DISTRICT OFFICER Login (Coimbatore)
def test_04_district_officer_scope():
    headers = get_auth_header("dist_tn_cbe", "district123")
    resp = client.get("/projects", headers=headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    for p in data:
        assert p["state_code"] == "TN"
        assert p["district_code"] == "TN-CBE"

# TEST 5: SEARCH Out-of-Scope Project
def test_05_search_out_of_scope():
    headers = get_auth_header("dist_tn_cbe", "district123")
    # Search for a project that exists in another state (e.g. MH)
    resp = client.get("/projects?search=MH-0002", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 0

# TEST 6: GIS MAP Scope Bounding
def test_06_gis_map_scope():
    headers = get_auth_header("state_tn", "state123")
    resp = client.get("/map/projects", headers=headers)
    assert resp.status_code == 200
    markers = resp.json()["data"]
    for m in markers:
        assert m["state_code"] == "TN"

# TEST 7: PDF REPORT Generation
def test_07_pdf_report_generation():
    headers = get_auth_header("admin", "admin123")
    resp = client.get("/reports/project/LG-TN-0042", headers=headers)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert len(resp.content) > 1000

# TEST 8: WHAT-IF SIMULATION
def test_08_what_if_simulation():
    headers = get_auth_header("admin", "admin123")
    sim_payload = {
        "project_id": "LG-TN-0042",
        "compensation_completion_pct": 90.0,
        "pending_legal_cases": 2,
        "approval_delay_days": 10
    }
    resp = client.post("/simulate", json=sim_payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["project_id"] == "LG-TN-0042"
    assert data["risk_reduction"] > 0.0, "Expected positive risk reduction delta"

# TEST 9: SHAP EXPLANATION
def test_09_shap_explanation():
    headers = get_auth_header("admin", "admin123")
    resp = client.get("/projects/LG-TN-0042/explanation", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "top_contributors" in data
    assert len(data["top_contributors"]) > 0

# TEST 10 & 11: ALERT & ACKNOWLEDGMENT
def test_10_and_11_alert_ack():
    headers = get_auth_header("admin", "admin123")
    # Fetch unread alert
    resp = client.get("/alerts?status_filter=UNREAD", headers=headers)
    assert resp.status_code == 200
    alerts = resp.json()["alerts"]
    assert len(alerts) > 0
    target_alert = alerts[0]["alert_id"]

    # Acknowledge
    ack_resp = client.put(f"/alerts/{target_alert}/acknowledge", headers=headers)
    assert ack_resp.status_code == 200
    assert ack_resp.json()["status"] == "ACKNOWLEDGED"

# TEST 12: INVALID LOGIN
def test_12_invalid_login():
    resp = client.post("/login", json={"username": "admin", "password": "wrongpassword123"})
    assert resp.status_code == 401
    assert "Invalid username or password" in resp.json()["detail"]

# TEST 13: AI ASSISTANT Scope-Aware Query
def test_13_ai_assistant_scope():
    headers = get_auth_header("dist_tn_cbe", "district123")
    resp = client.post("/ai-assistant/query", json={"query": "Which projects need immediate attention?"}, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "DISTRICT SCOPE" in data["scope_applied"]

# TEST 14 & 15: ANALYTICS SCOPE
def test_14_and_15_analytics_scope():
    # Admin gets all
    headers_adm = get_auth_header("admin", "admin123")
    resp_adm = client.get("/projects", headers=headers_adm)
    total_national = resp_adm.json()["total"]

    # State officer gets subset
    headers_tn = get_auth_header("state_tn", "state123")
    resp_tn = client.get("/projects", headers=headers_tn)
    total_tn = resp_tn.json()["total"]

    assert total_national > total_tn

# TEST 16: DATA VALIDATION SUMMARY
def test_16_dataset_integrity():
    p_cnt = execute_query_one("SELECT COUNT(*) AS cnt FROM projects")["cnt"]
    assert p_cnt >= 1000, "Dataset must contain at least 1000 projects"

    st_cnt = execute_query_one("SELECT COUNT(DISTINCT state_code) AS cnt FROM projects")["cnt"]
    assert st_cnt == 36, "Must cover all 28 states and 8 union territories (36 total)"

    fk_check = execute_query_one("PRAGMA foreign_key_check;")
    assert fk_check is None, "Foreign key integrity check must pass with 0 errors"
