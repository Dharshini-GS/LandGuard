"""
Alert Center Page for VISTRA.
Implements early-warning alert notifications, status updates, and project navigation. Zero emojis.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from backend.services.alert_service import get_alerts
from backend.database import execute_write
from backend.services.audit_service import log_action

def render_alerts_page(user: dict):
    st.markdown("## ALERT CENTER")
    st.caption("Early-warning signals requiring administrative attention.")

    c1, c2 = st.columns(2)
    with c1:
        status_filter = st.selectbox("Alert Status Filter", ["UNREAD", "ACKNOWLEDGED", "ALL"], key="alert_status_sel")
    with c2:
        severity_filter = st.selectbox("Severity Filter", ["ALL", "CRITICAL", "WARNING"], key="alert_sev_sel")

    try:
        data = get_alerts(user, status_filter=status_filter, severity_filter=severity_filter, limit=100)
    except Exception as e:
        st.error("ALERT DATA UNAVAILABLE: Unable to retrieve the latest alert information.")
        st.caption(f"Error details: {e}")
        if st.button("Retry Loading Alerts", key="btn_retry_alerts"):
            st.rerun()
        return

    # Top Summary Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Scope Alerts", data["total_alerts"])
    m2.metric("Unread Alerts", data["unread_count"])
    m3.metric("Critical Severity", data["critical_count"])
    m4.metric("Acknowledged Alerts", data["acknowledged_count"])

    st.markdown("---")

    alerts = data["alerts"]
    if not alerts:
        st.info("NO ACTIVE ALERTS — All monitored projects are currently below configured alert thresholds.")
        return

    st.caption(f"Displaying **{len(alerts)}** risk alerts matching current filters.")

    for r in alerts:
        a_id = r["alert_id"]
        p_id = r["project_id"]
        sev = r["severity"]
        status_val = r["status"]

        badge_cls = "badge-critical" if sev == "CRITICAL" else "badge-high"
        bg_color = "#FFFFFF" if status_val == "UNREAD" else "#F8FAFC"

        col_text, col_actions = st.columns([3.8, 1.2])

        with col_text:
            st.markdown(f"""
            <div class="kpi-card" style="background:{bg_color}; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b>{r['title']}</b>
                    <div>
                        <span class="{badge_cls}">{sev}</span>
                        <span style="font-size:10px; background:#E2E8F0; color:#334155; padding:2px 6px; border-radius:4px; margin-left:4px; font-weight:600;">{status_val}</span>
                    </div>
                </div>
                <div style="font-size:12px; color:#334155; margin-top:6px;">
                    {r['message']}
                </div>
                <div style="font-size:11px; color:#64748B; margin-top:6px; padding:6px; background:#F1F5F9; border-radius:4px;">
                    <b>Reason:</b> High risk probability ({r.get('risk_score', 0):.1f}%) in stage '{r.get('current_stage', 'N/A')}'.<br/>
                    <b>Recommended Action:</b> Prioritize nodal committee intervention and fast-track dispute resolution.<br/>
                    Project: <b>{p_id} ({r['project_name']})</b> | Location: {r['district_name']}, {r['state_name']} | Expected Delay: <b>{r.get('expected_delay_days', 0)} Days</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_actions:
            if st.button("View Project", key=f"btn_view_p_{a_id}", use_container_width=True):
                st.session_state["selected_project_id"] = p_id
                st.session_state["page"] = "Projects"
                st.rerun()

            if status_val == "UNREAD":
                if st.button("Mark Acknowledged", key=f"btn_ack_{a_id}", use_container_width=True):
                    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    execute_write("""
                    UPDATE alerts
                    SET status = 'ACKNOWLEDGED', acknowledged_by = ?, acknowledged_at = ?
                    WHERE alert_id = ?
                    """, (user["username"], ts, a_id))
                    log_action(user, "ACKNOWLEDGE_ALERT", project_id=p_id, details=f"Acknowledged alert {a_id}")
                    st.success("Alert Acknowledged!")
                    st.rerun()
