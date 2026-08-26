# 🛡️ LANDGUARD AI — Predict Before It Delays

> **SIH26017 — Predictive Analytics System for Early Detection of Land Acquisition Delays**

---

### **DATA TYPE: SYNTHETIC PROTOTYPE**

> *Prototype trained and demonstrated using synthetic/historical-like data. The system is designed to be retrained and validated using authorized government data when available.*

---

## 📌 Project Overview

**LANDGUARD AI** is an enterprise AI-powered early-warning decision-support platform designed for land acquisition infrastructure projects across India.

Instead of merely displaying where land acquisition is currently delayed, LANDGUARD AI:
1. **Predicts** where the next delay is likely to occur using XGBoost classifiers and regressors.
2. **Explains** why the delay is likely to occur using SHAP (SHapley Additive exPlanations) feature attribution.
3. **Simulates** policy interventions via interactive What-If scenario modeling.
4. **Prioritizes** multi-criteria tactical action items for nodal government officers.
5. **Enforces** strict database-level geographic and role-based access control (RBAC).

---

## 🏗️ Technology Stack

* **Frontend**: Streamlit, Plotly, Folium, streamlit-folium, Custom HTML/CSS
* **Backend**: FastAPI, Pydantic, SQLite (with `PRAGMA foreign_keys = ON`), SQLAlchemy / sqlite3 repository
* **Security & Auth**: Passlib (Bcrypt password hashing), JWT Session Tokens, Backend Scope Enforcement
* **Machine Learning**: Python, Scikit-Learn, XGBoost Classifier & Regressor, SHAP TreeExplainer, Joblib
* **PDF Reports**: ReportLab
* **Testing**: Pytest, FastAPI TestClient

---

## ⚡ Quick Start & Exact Execution Commands

Execute the following commands from a clean environment:

```bash
# 1. Create Virtual Environment
python -m venv .venv

# 2. Activate Environment (Windows)
.venv\Scripts\activate

# 3. Install Dependencies
pip install -r requirements.txt

# 4. Generate Synthetic Dataset (1,250+ projects across 36 States & UTs)
python scripts/generate_data.py

# 5. Validate Schema, Foreign Keys & Business Logic
python scripts/validate_data.py

# 6. Build SQLite Database & Foreign Key Indexes
python scripts/csv_to_sqlite.py

# 7. Train ML Models (XGBoost Classifier & Regressor + SHAP Explainer)
python scripts/train_model.py

# 8. Run Automated Acceptance & Security Test Suite
pytest tests/ -v

# 9. Start FastAPI Backend Server
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

# 10. Start Streamlit Frontend (In a separate terminal tab)
python -m streamlit run app.py
```

---

## 🔑 Demo Credentials

| Role | Username | Password | Authorized Scope | Description |
| :--- | :--- | :--- | :--- | :--- |
| **ADMIN** | `admin` | `admin123` | **NATIONAL** (All 36 States/UTs) | Full system administration, national analytics, audit logs, model retrain. |
| **STATE_OFFICER** | `state_tn` | `state123` | **STATE** (Tamil Nadu) | Restricted exclusively to Tamil Nadu state projects. |
| **DISTRICT_OFFICER** | `dist_tn_cbe` | `district123` | **DISTRICT** (Coimbatore) | Restricted exclusively to Coimbatore district projects. |
| **PROJECT_MANAGER** | `pm_user` | `pm123` | **PROJECT** (Assigned Projects) | Restricted to assigned project portfolio (includes `LG-TN-0042`). |
| **ANALYST** | `analyst` | `analyst123` | **NATIONAL** | Predictive analytics, model evaluation metrics, SHAP diagnostics. |

---

## 🛡️ Security & Authorization Architecture

Backend queries enforce scope restrictions at the database query layer:

* **STATE_OFFICER**: `WHERE state_code = current_user.state_code`
* **DISTRICT_OFFICER**: `WHERE state_code = current_user.state_code AND district_code = current_user.district_code`
* **PROJECT_MANAGER**: `WHERE project_id IN (authorized_project_ids)`
* **ADMIN**: National view (`1=1`)

> **Strict Security Guarantee**: Attempting to access an out-of-scope project via backend API or direct URL parameters yields an immediate **`HTTP 403 Forbidden`** response.

---

## 🎯 Target Demonstration Project (`LG-TN-0042`)

* **Project Name**: Highway Expansion - Coimbatore Section
* **Location**: Coimbatore, Tamil Nadu
* **Land Area**: 800 Acres | **Affected Families**: 450
* **Compensation Progress**: 42% Paid (261 Beneficiaries Pending)
* **Pending Legal Cases**: 18 Total Cases (14 Pending, 3 Judicial Stay Orders)
* **Clearance Approvals**: Environmental Clearance Pending (90 Days Delay)
* **ML Predicted Delay Risk**: **84.0% (CRITICAL)** | **Expected Delay**: 320 Days
* **What-If Simulation Result**: Increasing compensation disbursement to 90% drops predicted risk to **63.0%** (a **21.0 percentage point net reduction**).

---

## 📁 Repository Folder Structure

```text
LANDGUARD_AI/
│
├── app.py                      # Main Streamlit Entry Point & Navigation Shell
│
├── frontend/
│   ├── auth_ui.py              # Login Interface & Quick Demo Accounts
│   ├── components/             # Reusable UI Header, Scope Banner & Alerts Bell
│   ├── pages/                  # Page Modules (Dashboard, Projects, SHAP, What-If, GIS, etc.)
│   ├── styles/                 # Theme CSS (Government Portal Aesthetic)
│   └── utils.py                # Frontend Data Client & State Helpers
│
├── backend/
│   ├── main.py                 # FastAPI Application Server Entry
│   ├── auth.py                 # Password Hashing & JWT Authentication
│   ├── permissions.py          # Scope & Role Enforcement (SQL Filter Builder)
│   ├── database.py             # SQLite Connection Pool & Query Handlers
│   ├── schemas.py              # Pydantic Schemas
│   ├── routes/                 # FastAPI Router Modules
│   └── services/               # Core Services (ML Engine, PDF Service, Audit Logger)
│
├── data/                       # Generated CSV Dataset Files (14 CSVs + Geo Reference)
├── database/                   # SQLite Storage (`landguard.db`)
├── models/                     # Trained Model Artifacts (`delay_model.pkl`, `preprocessor.pkl`)
├── reports/                    # Generated Executive PDF Output Directory
│
├── scripts/
│   ├── generate_data.py        # Synthetic Dataset Generator
│   ├── validate_data.py        # Schema & Business Rule Integrity Validator
│   ├── csv_to_sqlite.py        # SQLite Database Builder with Foreign Key PRAGMA
│   ├── train_model.py          # Machine Learning Training Pipeline
│   └── update_model.py        # Model Re-training Trigger
│
├── tests/                      # Automated Acceptance Test Suite
├── utils/                      # Configurations, Geographic Reference Data, Logger
├── requirements.txt            # Dependency Requirements
└── README.md                   # System Documentation
```

---

## 🌐 API Endpoints

* `POST /login` — Authenticate user and issue JWT bearer token.
* `POST /logout` — Terminate session.
* `GET /me` — Fetch current user profile and scope credentials.
* `GET /projects` — Search, filter, sort, and paginate authorized projects.
* `GET /projects/{id}` — Retrieve detailed project file.
* `GET /projects/{id}/risk` — Predict project risk score and delay category.
* `GET /projects/{id}/stage-risk` — 11-stage lifecycle risk breakdown.
* `GET /projects/{id}/explanation` — SHAP feature attribution waterfall values.
* `POST /predict` — Run real-time model inference.
* `POST /simulate` — Run What-If scenario simulation.
* `GET /alerts` — Fetch active alerts filtered by scope.
* `PUT /alerts/{id}/acknowledge` — Acknowledge alert and log audit action.
* `GET /map/projects` — Fetch geospatial markers for interactive Folium GIS map.
* `GET /reports/project/{id}` — Compile and download executive ReportLab PDF report.
* `POST /ai-assistant/query` — Scope-aware natural language query assistant.
* `GET /admin/audit-logs` — Inspect security audit log records.
* `GET /admin/model/metrics` — View ML model precision, recall, ROC-AUC, and feature importance.
* `POST /admin/model/retrain` — Trigger model retraining pipeline.

---

## 📜 Synthetic Data Disclaimer

> LANDGUARD AI is a prototype system developed for demonstration purposes. All project records, beneficiary numbers, budget figures, legal dispute entries, and spatial points are synthetically generated representations designed to demonstrate predictive capabilities, explainability, and governance mechanisms. No real government records were fabricated.
