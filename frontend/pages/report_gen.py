"""
Report Generation Center Page for LANDGUARD AI.
Invokes ReportLab PDF generator service for authorized projects.
"""

import streamlit as st

from frontend.utils import fetch_filtered_projects
from backend.services.pdf_service import generate_project_pdf_report
from backend.permissions import verify_project_access

def render_report_gen_page(user: dict):
    st.markdown("## Executive PDF Report Generation Desk")

    projects = fetch_filtered_projects(user, limit=200)
    if not projects:
        st.info("No projects available within your authorized scope.")
        return

    p_ids = [p["project_id"] for p in projects]
    default_pid = st.session_state.get("selected_project_id", p_ids[0] if p_ids else "")
    if default_pid not in p_ids:
        default_pid = p_ids[0]

    selected_pid = st.selectbox("Select Project for PDF Report Compilation:", p_ids, index=p_ids.index(default_pid), key="rpt_proj_select")
    st.session_state["selected_project_id"] = selected_pid

    st.markdown(f"""
    <div class="kpi-card">
        <b>Target Project:</b> <code>{selected_pid}</code><br/>
        This action compiles an executive multi-page PDF risk assessment report containing:
        <ul>
            <li>Official Metadata & Scope Audit Signatures</li>
            <li>Predictive Delay Probability & Risk Severity Breakdown</li>
            <li>Acquisition Sub-System Progress Tables (Compensation, Legal, Approvals, R&R)</li>
            <li>Explainable AI (SHAP) Factor Attribution & Diagnostic Analysis</li>
            <li>Prioritized Tactical Recommendations</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Compile PDF Risk Report", type="primary", use_container_width=True, key="btn_compile_pdf_page"):
        try:
            verify_project_access(user, selected_pid)
            pdf_path = generate_project_pdf_report(selected_pid)
            st.success(f"PDF Report generated successfully for {selected_pid}!")

            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="Download Generated PDF File",
                    data=f.read(),
                    file_name=f"LANDGUARD_Risk_Report_{selected_pid}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="btn_download_pdf_final"
                )
        except Exception as e:
            st.error(f"Error compiling report: {e}")
