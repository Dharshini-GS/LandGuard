"""
SQLite Database Importer & Builder for VISTRA.
Creates database/VISTRA.db from data/*.csv files.
Enforces foreign key constraints and creates indexes for performance.
"""

import sys
import sqlite3
import csv
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from utils.config import DATA_DIR, DATABASE_PATH
from utils.logger import get_logger

logger = get_logger("DBBuilder")

def create_database():
    logger.info(f"Building SQLite database at: {DATABASE_PATH}")
    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Users Table
    cursor.execute("""
    CREATE TABLE users (
        user_id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL,
        scope_type TEXT NOT NULL,
        state_code TEXT,
        state_name TEXT,
        district_code TEXT,
        district_name TEXT,
        assigned_project_ids TEXT,
        status TEXT NOT NULL DEFAULT 'ACTIVE',
        created_at TEXT NOT NULL,
        last_login TEXT
    );
    """)

    # 2. Projects Table
    cursor.execute("""
    CREATE TABLE projects (
        project_id TEXT PRIMARY KEY,
        project_name TEXT NOT NULL,
        project_type TEXT NOT NULL,
        state_code TEXT NOT NULL,
        state_name TEXT NOT NULL,
        district_code TEXT NOT NULL,
        district_name TEXT NOT NULL,
        land_area_acres REAL NOT NULL,
        affected_families INTEGER NOT NULL,
        landowners_count INTEGER NOT NULL,
        budget_inr_cr REAL NOT NULL,
        current_stage TEXT NOT NULL,
        start_date TEXT NOT NULL,
        target_completion_date TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)

    # 3. Land Parcels Table
    cursor.execute("""
    CREATE TABLE land_parcels (
        parcel_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        parcel_number TEXT NOT NULL,
        area_acres REAL NOT NULL,
        ownership_type TEXT NOT NULL,
        verified_flag INTEGER NOT NULL,
        dispute_flag INTEGER NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
    );
    """)

    # 4. Lifecycle Timeline Table
    cursor.execute("""
    CREATE TABLE lifecycle_timeline (
        timeline_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        stage_name TEXT NOT NULL,
        planned_duration_days INTEGER NOT NULL,
        actual_duration_days INTEGER NOT NULL,
        stage_status TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
    );
    """)

    # 5. Compensation Table
    cursor.execute("""
    CREATE TABLE compensation (
        comp_id TEXT PRIMARY KEY,
        project_id TEXT UNIQUE NOT NULL,
        beneficiaries_total INTEGER NOT NULL,
        beneficiaries_paid INTEGER NOT NULL,
        beneficiaries_pending INTEGER NOT NULL,
        amount_sanctioned_cr REAL NOT NULL,
        amount_disbursed_cr REAL NOT NULL,
        disbursement_percentage REAL NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
    );
    """)

    # 6. Legal Disputes Table
    cursor.execute("""
    CREATE TABLE legal_disputes (
        dispute_id TEXT PRIMARY KEY,
        project_id TEXT UNIQUE NOT NULL,
        total_cases INTEGER NOT NULL,
        court_district_cases INTEGER NOT NULL,
        court_high_cases INTEGER NOT NULL,
        court_supreme_cases INTEGER NOT NULL,
        pending_cases INTEGER NOT NULL,
        resolved_cases INTEGER NOT NULL,
        stay_orders_count INTEGER NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
    );
    """)

    # 7. Approvals Table
    cursor.execute("""
    CREATE TABLE approvals (
        approval_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        approval_type TEXT NOT NULL,
        status TEXT NOT NULL,
        submission_date TEXT NOT NULL,
        approval_date TEXT,
        delay_days INTEGER NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
    );
    """)

    # 8. Documentation Table
    cursor.execute("""
    CREATE TABLE documentation (
        doc_id TEXT PRIMARY KEY,
        project_id TEXT UNIQUE NOT NULL,
        total_records INTEGER NOT NULL,
        records_verified INTEGER NOT NULL,
        records_pending INTEGER NOT NULL,
        title_clearance_percentage REAL NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
    );
    """)

    # 9. Rehabilitation R&R Table
    cursor.execute("""
    CREATE TABLE rehabilitation_rr (
        rr_id TEXT PRIMARY KEY,
        project_id TEXT UNIQUE NOT NULL,
        families_eligible INTEGER NOT NULL,
        families_rehabilitated INTEGER NOT NULL,
        families_pending INTEGER NOT NULL,
        site_readiness_percentage REAL NOT NULL,
        grant_disbursed_cr REAL NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
    );
    """)

    # 10. Stakeholders Table
    cursor.execute("""
    CREATE TABLE stakeholders (
        stakeholder_id TEXT PRIMARY KEY,
        project_id TEXT UNIQUE NOT NULL,
        objections_received INTEGER NOT NULL,
        objections_resolved INTEGER NOT NULL,
        pending_objections INTEGER NOT NULL,
        public_hearing_status TEXT NOT NULL,
        stakeholder_response_index REAL NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
    );
    """)

    # 11. Administrative Performance Table
    cursor.execute("""
    CREATE TABLE administrative_performance (
        admin_id TEXT PRIMARY KEY,
        project_id TEXT UNIQUE NOT NULL,
        nodal_officer_assigned TEXT NOT NULL,
        dept_workload_score REAL NOT NULL,
        sla_compliance_percentage REAL NOT NULL,
        bottleneck_score REAL NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
    );
    """)

    # 12. Project Geospatial Table
    cursor.execute("""
    CREATE TABLE project_geospatial (
        geo_id TEXT PRIMARY KEY,
        project_id TEXT UNIQUE NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        boundary_geojson TEXT NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
    );
    """)

    # 13. Project Outcomes Table
    cursor.execute("""
    CREATE TABLE project_outcomes (
        outcome_id TEXT PRIMARY KEY,
        project_id TEXT UNIQUE NOT NULL,
        delay_flag INTEGER NOT NULL,
        delay_days INTEGER NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
    );
    """)

    # 14. Risk History Table
    cursor.execute("""
    CREATE TABLE risk_history (
        history_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        prediction_date TEXT NOT NULL,
        delay_probability REAL NOT NULL,
        risk_score REAL NOT NULL,
        risk_category TEXT NOT NULL,
        expected_delay_days INTEGER NOT NULL,
        highest_risk_stage TEXT NOT NULL,
        model_version TEXT NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
    );
    """)

    # --- Operational Tables ---
    # Alerts Table
    cursor.execute("""
    CREATE TABLE alerts (
        alert_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        alert_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'UNREAD',
        created_at TEXT NOT NULL,
        acknowledged_by TEXT,
        acknowledged_at TEXT,
        FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
    );
    """)

    # Simulations Table
    cursor.execute("""
    CREATE TABLE simulations (
        sim_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        parameters_json TEXT NOT NULL,
        initial_risk_score REAL NOT NULL,
        simulated_risk_score REAL NOT NULL,
        risk_reduction REAL NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    """)

    # Audit Logs Table
    cursor.execute("""
    CREATE TABLE audit_logs (
        log_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        username TEXT NOT NULL,
        role TEXT NOT NULL,
        scope_type TEXT NOT NULL,
        action TEXT NOT NULL,
        project_id TEXT,
        details TEXT NOT NULL,
        timestamp TEXT NOT NULL
    );
    """)

    # Login History Table
    cursor.execute("""
    CREATE TABLE login_history (
        login_id TEXT PRIMARY KEY,
        username TEXT NOT NULL,
        success_flag INTEGER NOT NULL,
        ip_address TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        details TEXT
    );
    """)

    conn.commit()

    # Import CSV Data
    import_csv(cursor, "users", "users.csv")
    import_csv(cursor, "projects", "projects.csv")
    import_csv(cursor, "land_parcels", "land_parcels.csv")
    import_csv(cursor, "lifecycle_timeline", "lifecycle_timeline.csv")
    import_csv(cursor, "compensation", "compensation.csv")
    import_csv(cursor, "legal_disputes", "legal_disputes.csv")
    import_csv(cursor, "approvals", "approvals.csv")
    import_csv(cursor, "documentation", "documentation.csv")
    import_csv(cursor, "rehabilitation_rr", "rehabilitation_rr.csv")
    import_csv(cursor, "stakeholders", "stakeholders.csv")
    import_csv(cursor, "administrative_performance", "administrative_performance.csv")
    import_csv(cursor, "project_geospatial", "project_geospatial.csv")
    import_csv(cursor, "project_outcomes", "project_outcomes.csv")
    import_csv(cursor, "risk_history", "risk_history.csv")

    # Populate initial alerts from high/critical risk history
    cursor.execute("""
    SELECT r.project_id, r.risk_category, r.risk_score, p.project_name, p.state_code
    FROM risk_history r
    JOIN projects p ON r.project_id = p.project_id
    WHERE r.risk_category IN ('HIGH', 'CRITICAL')
    LIMIT 150;
    """)

    critical_rows = cursor.fetchall()
    alert_count = 1
    for p_id, r_cat, r_score, p_name, st_code in critical_rows:
        severity = "CRITICAL" if r_cat == "CRITICAL" else "WARNING"
        alert_type = "CRITICAL_RISK" if r_cat == "CRITICAL" else "RISK_INCREASE"
        title = f"Critical Risk Alert: {p_id}" if r_cat == "CRITICAL" else f"Elevated Risk Warning: {p_id}"
        msg = f"Project '{p_name}' has reached a risk score of {r_score:.1f}% ({r_cat}). Immediate intervention required."
        cursor.execute("""
        INSERT INTO alerts (alert_id, project_id, alert_type, severity, title, message, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, 'UNREAD', '2024-02-25 09:00:00')
        """, (f"ALT-{alert_count:04d}", p_id, alert_type, severity, title, msg))
        alert_count += 1

    # Create Indexes
    cursor.execute("CREATE INDEX idx_projects_state ON projects(state_code);")
    cursor.execute("CREATE INDEX idx_projects_district ON projects(district_code);")
    cursor.execute("CREATE INDEX idx_projects_type ON projects(project_type);")
    cursor.execute("CREATE INDEX idx_projects_stage ON projects(current_stage);")
    cursor.execute("CREATE INDEX idx_projects_status ON projects(status);")
    cursor.execute("CREATE INDEX idx_risk_hist_project ON risk_history(project_id);")
    cursor.execute("CREATE INDEX idx_risk_hist_cat ON risk_history(risk_category);")
    cursor.execute("CREATE INDEX idx_alerts_project ON alerts(project_id);")

    conn.commit()

    # Integrity check
    cursor.execute("PRAGMA integrity_check;")
    res = cursor.fetchone()[0]
    logger.info(f"SQLite PRAGMA integrity_check result: {res}")

    # Statistics
    cursor.execute("SELECT COUNT(*) FROM projects;")
    tot_p = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users;")
    tot_u = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM alerts;")
    tot_a = cursor.fetchone()[0]

    logger.info(f"Database build complete. Projects: {tot_p}, Users: {tot_u}, Alerts: {tot_a}.")
    conn.close()

def import_csv(cursor, table_name, csv_filename):
    filepath = DATA_DIR / csv_filename
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
        placeholders = ", ".join(["?"] * len(headers))
        col_names = ", ".join(headers)
        sql = f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})"
        rows = list(reader)
        cursor.executemany(sql, rows)
    logger.info(f"Imported {len(rows)} rows into '{table_name}' table.")

if __name__ == "__main__":
    create_database()
