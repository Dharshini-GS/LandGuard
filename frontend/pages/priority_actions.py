"""
Priority Ranking & Action Recommendations Page for VISTRA.
Features multi-criteria priority matrix, action briefs, and CSV export.
"""

import streamlit as st
import pandas as pd

from frontend.utils import fetch_filtered_projects

def render_priority_actions_page(user: dict):
    st.markdown("## Intervention Priority Matrix & Tactical Action Desk")

    projects = fetch_filtered_projects(user, limit=300)
    if not projects:
        st.info("No projects available within your authorized scope.")
        return

    df = pd.DataFrame(projects)
    df = df.sort_values("priority_score", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1

    col_title, col_export = st.columns([3, 1])

    with col_title:
        st.markdown("#### Top Priority Projects Requiring Nodal Intervention")

    with col_export:
        csv_data = df[["rank", "project_id", "project_name", "state_name", "district_name", "current_stage", "risk_category", "risk_score", "expected_delay_days", "priority_score"]].to_csv(index=False)
        st.download_button(
            label="Export Action Plan (CSV)",
            data=csv_data,
            file_name="VISTRA_Action_Plan.csv",
            mime="text/csv",
            use_container_width=True,
            key="btn_export_action_csv"
        )

    st.dataframe(
        df[["rank", "project_id", "project_name", "state_name", "district_name", "current_stage", "risk_category", "risk_score", "expected_delay_days", "priority_score"]],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    st.subheader("Top Priority Action Briefs")

    top_5 = df.head(5)
    for _, row in top_5.iterrows():
        p_id = row["project_id"]
        cat = row["risk_category"]
        badge_cls = "badge-critical" if cat == "CRITICAL" else ("badge-high" if cat == "HIGH" else "badge-medium")

        st.markdown(f"""
        <div class="kpi-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <span style="font-size:16px; font-weight:800; color:#0F172A;">Rank #{row['rank']}: {p_id}</span> — <b>{row['project_name']}</b>
                    <div style="font-size:12px; color:#64748B;">State: {row['state_name']} | District: {row['district_name']} | Stage: {row['current_stage']}</div>
                </div>
                <div>
                    <span class="{badge_cls}">{cat} ({row['risk_score']}%)</span>
                </div>
            </div>
            <div style="margin-top:10px; padding:10px; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:4px; font-size:12px; color:#334155;">
                <b>Primary Delay Driver:</b> Pending Court Stay Orders & Compensation Disbursement Delay<br/>
                <b>Recommended Action:</b> Form joint district revenue-legal committee to expedite stay order hearings and clear beneficiary direct payments.<br/>
                <b>Priority Score:</b> {row['priority_score']} | Expected Delay: {row['expected_delay_days']} Days
            </div>
        </div>
        """, unsafe_allow_html=True)
