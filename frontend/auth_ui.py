"""
Secure Login Access Portal for VISTRA.
Executive login portal with Vistra branding, shield logo, and 5 one-click demo access profiles.
"""

import streamlit as st
import os
from frontend.utils import login_user

DEMO_PROFILES = [
    {
        "role_label": "🛡️ ADMIN",
        "username": "admin",
        "password": "admin123",
        "scope": "National (All 36 States/UTs)",
        "badge": "NATIONAL"
    },
    {
        "role_label": "🏛️ STATE OFFICER",
        "username": "state_tn",
        "password": "state123",
        "scope": "State (Tamil Nadu)",
        "badge": "STATE"
    },
    {
        "role_label": "📍 DISTRICT OFFICER",
        "username": "dist_tn_cbe",
        "password": "district123",
        "scope": "District (Coimbatore)",
        "badge": "DISTRICT"
    },
    {
        "role_label": "📁 PROJECT MANAGER",
        "username": "pm_user",
        "password": "pm123",
        "scope": "Project Portfolio (LG-TN-0042)",
        "badge": "PROJECT"
    },
    {
        "role_label": "📊 ANALYST",
        "username": "analyst",
        "password": "analyst123",
        "scope": "National Predictive Analytics",
        "badge": "ANALYST"
    }
]

def render_login_page():
    # Centered Header Branding & Vistra Shield Logo
    st.markdown("""
    <div style="text-align: center; margin-top: 20px; margin-bottom: 20px;">
    """, unsafe_allow_html=True)
    
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "vistra_logo.png")
    if os.path.exists(logo_path):
        col_l1, col_l2, col_l3 = st.columns([1.5, 1, 1.5])
        with col_l2:
            st.image(logo_path, use_container_width=True)
    
    st.markdown("""
        <div style="font-size: 36px; font-weight: 800; color: #0F172A; letter-spacing: -0.5px; margin-top: 8px;">VISTRA</div>
        <div style="font-size: 15px; font-weight: 700; color: #166534; margin-top: 2px;">Predict Before It Delays.</div>
        <div style="font-size: 13px; color: #64748B; margin-top: 4px;">Predictive Analytics System for Early Detection of Land Acquisition Delays</div>
    </div>
    """, unsafe_allow_html=True)

    # 5 Demo Profiles Quick Selector Bar
    st.markdown("""
    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 16px 20px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
        <div style="font-size: 12px; font-weight: 800; color: #1E4D2B; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 10px; display: flex; align-items: center; gap: 6px;">
            🔑 ONE-CLICK DEMO ACCESS PROFILES (SELECT ANY ROLE TO SIGN IN INSTANTLY)
        </div>
    """, unsafe_allow_html=True)

    d_cols = st.columns(5)
    for idx, profile in enumerate(DEMO_PROFILES):
        with d_cols[idx]:
            st.markdown(f"""
            <div style="font-size: 11px; font-weight: 700; color: #0F172A; margin-bottom: 4px;">{profile['role_label']}</div>
            <div style="font-size: 10px; color: #64748B; margin-bottom: 6px; min-height: 28px;">{profile['scope']}</div>
            """, unsafe_allow_html=True)
            if st.button(f"Login as {profile['badge']}", key=f"btn_quick_demo_{idx}", use_container_width=True, type="secondary"):
                with st.spinner(f"Signing in as {profile['role_label']}..."):
                    user = login_user(profile['username'], profile['password'])
                    if user:
                        st.session_state["input_uname"] = profile['username']
                        st.session_state["input_pwd"] = profile['password']
                        st.success(f"Authenticated as {user['full_name']}")
                        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # Manual Credentials Sign-In Form
    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:
        st.markdown("""
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.04);">
            <h4 style='color:#0F172A; font-size:14px; font-weight:800; margin-bottom:4px; text-transform:uppercase; letter-spacing:0.8px;'>AUTHORIZED MANUAL SIGN IN</h4>
        """, unsafe_allow_html=True)
        st.caption("Enter custom credentials to access VISTRA services.")

        username_input = st.text_input("Username", placeholder="Enter username", key="input_uname", value=st.session_state.get("input_uname", ""))
        password_input = st.text_input("Password", type="password", placeholder="Enter password", key="input_pwd", value=st.session_state.get("input_pwd", ""))

        st.markdown("<br/>", unsafe_allow_html=True)
        if st.button("SIGN IN TO VISTRA", type="primary", use_container_width=True, key="btn_login_submit"):
            if not username_input or not password_input:
                st.error("INVALID CREDENTIALS: Username and password are required.")
            else:
                with st.spinner("SIGNING IN..."):
                    user = login_user(username_input, password_input)
                    if user:
                        st.success(f"Authenticated as {user['full_name']}")
                        st.rerun()
                    else:
                        st.error("INVALID CREDENTIALS: Username or password is incorrect. Please verify your credentials and try again.")

        st.markdown("""
        </div>
        <div style="text-align: center; margin-top: 24px; font-size: 11px; color: #94A3B8;">
            Authorized users only | VISTRA &bull; Predictive Decision Support Platform<br/>
            <span style="color:#16A34A; font-weight:600;">System Status: Operational</span>
        </div>
        """, unsafe_allow_html=True)

