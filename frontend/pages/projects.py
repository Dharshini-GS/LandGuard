"""
Projects Explorer, Creation & Detail Editing Page for LANDGUARD AI.
Enables searching, viewing, adding new projects, updating project details, and binary PDF downloading. Zero emojis.
"""

import streamlit as st
import pandas as pd
import random
from pathlib import Path

from frontend.utils import fetch_filtered_projects
from backend.permissions import verify_project_access
from backend.services.ml_service import ml_service_instance
from backend.database import execute_query_one, execute_query, execute_write
from backend.services.pdf_service import generate_project_pdf_report
from backend.services.audit_service import log_action
from utils.geo_data import GEO_REFERENCE, PROJECT_TYPES, LIFECYCLE_STAGES

def render_projects_page(user: dict):
    st.markdown("## Land Acquisition Projects Explorer & Management")

    # Action Bar: Search/Filter + Add/Update Project Buttons
    tab_exp, tab_add, tab_upd = st.tabs(["Projects Directory", "+ Add New Project", "Update Existing Project"])

    with tab_exp:
        _render_projects_directory_tab(user)

    with tab_add:
        _render_add_project_tab(user)

    with tab_upd:
        _render_update_project_tab(user)

def _render_projects_directory_tab(user: dict):
    # Search & Filter bar
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])

    with c1:
        search_query = st.text_input("Search Projects", placeholder="Search by Project ID, Name, Sector...", key="proj_search_input")

    with c2:
        state_list = ["ALL"] + sorted(list(GEO_REFERENCE.keys()))
        selected_state = st.selectbox("State / UT", state_list, key="proj_filter_state")

    with c3:
        risk_list = ["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"]
        selected_risk = st.selectbox("Risk Category", risk_list, key="proj_filter_risk")

    with c4:
        stage_list = ["ALL"] + LIFECYCLE_STAGES
        selected_stage = st.selectbox("Current Stage", stage_list, key="proj_filter_stage")

    st_filter = None if selected_state == "ALL" else selected_state
    rk_filter = None if selected_risk == "ALL" else selected_risk
    stg_filter = None if selected_stage == "ALL" else selected_stage

    projects = fetch_filtered_projects(
        user,
        search=search_query,
        state=st_filter,
        risk_cat=rk_filter,
        stage=stg_filter,
        limit=300
    )

    if not projects:
        st.info("No projects found within your authorized scope matching the criteria.")
        return

    df = pd.DataFrame(projects)
    st.caption(f"Showing **{len(df)}** authorized projects matching your scope.")

    proj_ids = df["project_id"].tolist()
    default_idx = proj_ids.index("LG-TN-0042") if "LG-TN-0042" in proj_ids else 0

    selected_pid = st.selectbox("Select Project for Detailed Inspection:", proj_ids, index=default_idx, key="proj_select_dropdown")

    st.dataframe(
        df[["project_id", "project_name", "state_name", "district_name", "project_type", "current_stage", "risk_category", "risk_score", "expected_delay_days", "priority_score"]],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    if selected_pid:
        _render_project_detail_panel(user, selected_pid)

def _render_add_project_tab(user: dict):
    st.markdown("### Register New Land Acquisition Project")
    st.caption("Create a new project entry in the central registry. ML risk scoring will be automatically calculated.")

    with st.form("form_add_new_project"):
        c1, c2 = st.columns(2)
        with c1:
            p_name = st.text_input("Project Name", placeholder="e.g. Chennai Multi-Modal Freight Corridor")
            state_keys = sorted(list(GEO_REFERENCE.keys()))
            p_state = st.selectbox("State / UT", state_keys)
            dist_list = GEO_REFERENCE.get(p_state, ["Central District"])
            p_dist = st.selectbox("District Name", dist_list)
            p_type = st.selectbox("Project Sector", PROJECT_TYPES)
        with c2:
            p_stage = st.selectbox("Initial Lifecycle Stage", LIFECYCLE_STAGES)
            p_area = st.number_input("Total Land Area Required (Hectares)", min_value=1.0, value=150.0, step=10.0)
            p_parcels = st.number_input("Number of Land Parcels", min_value=1, value=450, step=10)
            p_families = st.number_input("Affected Families Count", min_value=0, value=220, step=10)

        submitted = st.form_submit_button("REGISTER PROJECT", type="primary", use_container_width=True)

        if submitted:
            if not p_name:
                st.error("Project Name is required.")
                return

            state_code = p_state[:2].upper()
            rand_id = random.randint(1000, 9999)
            new_pid = f"LG-{state_code}-{rand_id}"

            sql_insert = """
            INSERT INTO projects (
                project_id, project_name, state_name, district_name, project_type,
                current_stage, target_completion_days, total_land_required_ha,
                total_parcels, affected_families, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """
            execute_write(sql_insert, (
                new_pid, p_name, p_state, p_dist, p_type,
                p_stage, 365, p_area, p_parcels, p_families
            ))

            ml_service_instance.predict_risk(new_pid)
            log_action(user, "CREATE_PROJECT", details=f"Created project {new_pid}: {p_name}")

            st.success(f"Project **{new_pid}** successfully registered and ingested into risk engine!")
            st.rerun()

def _render_update_project_tab(user: dict):
    st.markdown("### Update Existing Project Record")

    projects = fetch_filtered_projects(user, limit=500)
    if not projects:
        st.warning("No projects available to update.")
        return

    p_ids = [p["project_id"] for p in projects]
    upd_pid = st.selectbox("Select Project to Update:", p_ids, key="upd_select_pid")

    curr_p = execute_query_one("SELECT * FROM projects WHERE project_id = ?", (upd_pid,))
    if not curr_p:
        st.error("Project not found.")
        return

    with st.form("form_update_project"):
        c1, c2 = st.columns(2)
        with c1:
            u_name = st.text_input("Project Name", value=curr_p["project_name"])
            u_stage = st.selectbox("Current Stage", LIFECYCLE_STAGES, index=LIFECYCLE_STAGES.index(curr_p["current_stage"]) if curr_p["current_stage"] in LIFECYCLE_STAGES else 0)
        with c2:
            u_area = st.number_input("Land Area Required (ha)", value=float(curr_p.get("total_land_required_ha", 100.0)))
            u_families = st.number_input("Affected Families", value=int(curr_p.get("affected_families", 50)))

        submit_upd = st.form_submit_button("UPDATE PROJECT DETAILS", type="primary", use_container_width=True)

        if submit_upd:
            execute_write("""
            UPDATE projects
            SET project_name = ?, current_stage = ?, total_land_required_ha = ?, affected_families = ?, updated_at = CURRENT_TIMESTAMP
            WHERE project_id = ?
            """, (u_name, u_stage, u_area, u_families, upd_pid))

            ml_service_instance.predict_risk(upd_pid)
            log_action(user, "UPDATE_PROJECT", details=f"Updated project {upd_pid}")

            st.success(f"Project **{upd_pid}** updated successfully!")
            st.rerun()

def _render_project_detail_panel(user: dict, project_id: str):
    st.markdown(f"### Project Intelligence File: `{project_id}`")

    try:
        verify_project_access(user, project_id)
    except Exception as e:
        st.error("Access Denied: Project outside your authorized scope.")
        return

    proj = execute_query_one("SELECT * FROM projects WHERE project_id = ?", (project_id,))
    risk_info = ml_service_instance.predict_risk(project_id)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Project Name", proj["project_name"])
    c2.metric("Location", f"{proj['district_name']}, {proj['state_name']}")
    c3.metric("Predicted Risk", f"{risk_info['risk_score']:.1f}%")
    c4.metric("Expected Delay", f"{risk_info['expected_delay_days']} Days")

    pdf_res = generate_project_pdf_report(project_id)

    if isinstance(pdf_res, (str, Path)):
        pdf_bytes = Path(pdf_res).read_bytes()
    else:
        pdf_bytes = pdf_res

    st.download_button(
        label=f"DOWNLOAD PROJECT PDF REPORT ({project_id})",
        data=pdf_bytes,
        file_name=f"LANDGUARD_Report_{project_id}.pdf",
        mime="application/pdf",
        key=f"btn_dl_proj_{project_id}"
    )
