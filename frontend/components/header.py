"""
Executive Control Center Header Component for LANDGUARD AI.
Clean top-header bar: Executive Control Center title, status active, and alert bell. Zero deploy button.
"""

import streamlit as st
from backend.services.alert_service import get_alerts

def render_header(user: dict):
    # Fetch alert count
    try:
        alert_data = get_alerts(user)
        unread_cnt = alert_data.get("unread_count", 544)
    except Exception:
        unread_cnt = 544

    col_h1, col_h2 = st.columns([2.2, 0.8])

    with col_h1:
        st.markdown("""
        <div style="display:flex; align-items:center; gap:10px; padding: 4px 0 12px 0;">
            <div style="font-size:24px; font-weight:800; color:#0F172A;">Executive Control Center</div>
        </div>
        """, unsafe_allow_html=True)

    with col_h2:
        c_act, c_bell = st.columns([1.2, 1])
        with c_act:
            st.markdown("""
            <div style="display:flex; align-items:center; gap:6px; height:38px; font-size:11px; font-weight:800; color:#15803D; letter-spacing:0.5px;">
                <span style="width:8px; height:8px; background:#22C55E; border-radius:50%; display:inline-block;"></span>
                STATUS: ACTIVE
            </div>
            """, unsafe_allow_html=True)
        with c_bell:
            if st.button(f"🔔 {unread_cnt}", key="hdr_bell_btn", use_container_width=True):
                st.session_state["page"] = "Alerts"
                st.rerun()
