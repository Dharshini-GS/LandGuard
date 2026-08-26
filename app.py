"""
LANDGUARD AI — Main Command Center Application Entry Point.
Predict Before It Delays.
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Streamlit Page Setup
st.set_page_config(
    page_title="LANDGUARD AI — Government Intelligence Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

from frontend.styles.theme import apply_custom_theme
from frontend.auth_ui import render_login_page
from frontend.components.header import render_header
from frontend.components.sidebar import render_enterprise_sidebar
from frontend.components.ai_drawer import render_floating_ai_assistant
from frontend.utils import get_current_session_user

from frontend.pages.dashboard import render_dashboard_page
from frontend.pages.projects import render_projects_page
from frontend.pages.risk_analysis import render_risk_analysis_page
from frontend.pages.stage_risk import render_stage_risk_page
from frontend.pages.explainable_ai import render_explainable_ai_page
from frontend.pages.priority_actions import render_priority_actions_page
from frontend.pages.what_if_sim import render_what_if_page
from frontend.pages.alerts_view import render_alerts_page
from frontend.pages.gis_map import render_gis_map_page
from frontend.pages.analytics_view import render_analytics_page
from frontend.pages.report_gen import render_report_gen_page
from frontend.pages.admin_view import render_admin_page

# Apply Enterprise Custom Theme CSS
apply_custom_theme()

def main():
    user = get_current_session_user()

    # 1. Authentication Gatekeeper — No application data visible before login
    if not user:
        render_login_page()
        return

    # 2. Render Executive Header & Scope Indicator
    render_header(user)

    # 3. Render Enterprise Dark Sidebar & Router Dispatch
    selected_page = render_enterprise_sidebar(user)

    # 4. Modular Page Router Dispatch
    if selected_page == "Dashboard":
        render_dashboard_page(user)
    elif selected_page == "Projects":
        render_projects_page(user)
    elif selected_page == "Risk Analysis":
        render_risk_analysis_page(user)
    elif selected_page == "Stage-wise Risk":
        render_stage_risk_page(user)
    elif selected_page == "Explainable AI":
        render_explainable_ai_page(user)
    elif selected_page == "Priority & Actions":
        render_priority_actions_page(user)
    elif selected_page == "What-If Simulator":
        render_what_if_page(user)
    elif selected_page == "Alerts":
        render_alerts_page(user)
    elif selected_page == "GIS Risk Map":
        render_gis_map_page(user)
    elif selected_page == "Analytics":
        render_analytics_page(user)
    elif selected_page == "Reports":
        render_report_gen_page(user)
    elif selected_page == "Administration":
        render_admin_page(user)
    else:
        render_dashboard_page(user)

    # 5. Render Floating AI Assistant Popover (Bottom-Right on all pages)
    render_floating_ai_assistant(user)

if __name__ == "__main__":
    main()
