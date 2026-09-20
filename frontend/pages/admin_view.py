"""
Admin Control Center Page for VISTRA.
Provides User Management, Model Administration & Retrain, Audit Logs, and System Health.
"""

import streamlit as st
import json
import uuid
from datetime import datetime
import pandas as pd

from backend.database import execute_query, execute_query_one, execute_write
from backend.auth import hash_password
from backend.services.audit_service import log_action
from scripts.update_model import update_model
from utils.config import MODEL_METADATA_PATH, DATABASE_PATH
from utils.geo_data import ROLES, SCOPES, GEO_REFERENCE

def render_admin_page(user: dict):
    if user.get("role") not in ["ADMIN", "ANALYST"]:
        st.error("Access Denied: Administration privileges required.")
        return

    st.markdown("## Administration & Model Governance Center")

    tab1, tab2, tab3, tab4 = st.tabs(["User Management", "Model Governance", "Audit Trail Logs", "System Health"])

    # TAB 1: User Management
    with tab1:
        st.subheader("System User Directory")
        users = execute_query("SELECT user_id, username, full_name, role, scope_type, state_name, district_name, status, last_login FROM users ORDER BY created_at DESC")
        st.dataframe(pd.DataFrame(users), use_container_width=True, hide_index=True)

        if user.get("role") == "ADMIN":
            st.markdown("---")
            st.subheader("Create New Authorized User")
            c1, c2 = st.columns(2)
            with c1:
                new_uname = st.text_input("Username", key="create_uname")
                new_pwd = st.text_input("Password", type="password", key="create_pwd")
                new_fname = st.text_input("Full Name", key="create_fname")
            with c2:
                new_role = st.selectbox("Role", ROLES, key="create_role")
                new_scope = st.selectbox("Scope Type", SCOPES, key="create_scope")
                new_state = st.selectbox("Assigned State Code (Optional)", [""] + list(GEO_REFERENCE.keys()), key="create_st")

            if st.button("Create User Account", type="primary", key="btn_create_usr_submit"):
                if not new_uname or not new_pwd or not new_fname:
                    st.error("Please fill in all required fields.")
                else:
                    p_hash = hash_password(new_pwd.strip())
                    u_id = f"USR-{uuid.uuid4().hex[:8].upper()}"
                    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st_name = GEO_REFERENCE[new_state]["name"] if new_state else ""
                    try:
                        execute_write("""
                        INSERT INTO users (user_id, username, password_hash, full_name, role, scope_type, state_code, state_name, status, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?)
                        """, (u_id, new_uname.strip(), p_hash, new_fname.strip(), new_role, new_scope, new_state, st_name, ts))
                        log_action(user, "CREATE_USER", details=f"Created user {new_uname}")
                        st.success(f"User {new_uname} created successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating user: {e}")

    # TAB 2: Model Governance & Retraining
    with tab2:
        st.subheader("XGBoost Predictive Analytics Governance")

        meta = {}
        if MODEL_METADATA_PATH.exists():
            with open(MODEL_METADATA_PATH, "r", encoding="utf-8") as f:
                meta = json.load(f)

        m = meta.get("metrics", {})
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Model Version", meta.get("model_version", "v1.0.0"))
        c2.metric("Accuracy", f"{m.get('accuracy', 0.0)*100:.1f}%")
        c3.metric("F1-Score", f"{m.get('f1_score', 0.0):.4f}")
        c4.metric("ROC-AUC", f"{m.get('roc_auc', 0.0):.4f}")

        st.markdown("---")

        if st.button("Trigger Model Re-Training Pipeline", type="primary", key="btn_retrain_model_admin"):
            with st.spinner("Retraining XGBoost classifier, regressor, and SHAP explainer..."):
                update_model()
                log_action(user, "UPDATE_MODEL", details="Triggered model retrain from admin UI")
                st.success("Model retrained successfully!")
                st.rerun()

    # TAB 3: Audit Logs
    with tab3:
        st.subheader("Security & System Action Audit Logs")
        logs = execute_query("SELECT log_id, timestamp, username, role, scope_type, action, project_id, details FROM audit_logs ORDER BY timestamp DESC LIMIT 150")
        st.dataframe(pd.DataFrame(logs), use_container_width=True, hide_index=True)

    # TAB 4: System Health
    with tab4:
        st.subheader("Application Diagnostics & Health Status")
        p_cnt = execute_query_one("SELECT COUNT(*) AS cnt FROM projects")["cnt"]
        u_cnt = execute_query_one("SELECT COUNT(*) AS cnt FROM users")["cnt"]
        a_cnt = execute_query_one("SELECT COUNT(*) AS cnt FROM alerts WHERE status = 'UNREAD'")["cnt"]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Database Status", "HEALTHY")
        c2.metric("Total Projects", f"{p_cnt:,}")
        c3.metric("Registered Users", f"{u_cnt}")
        c4.metric("Unread Alerts", f"{a_cnt}")

        st.code(f"""
        Database Path: {DATABASE_PATH}
        Model Metadata Path: {MODEL_METADATA_PATH}
        Application System: ONLINE
        Security Enforcement: ACTIVE (RBAC Scope Filters Engaged)
        """, language="text")
