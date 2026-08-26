"""
Secure Login Access Portal for LANDGUARD AI.
Clean, executive login portal with clear visual hierarchy and primary blue sign-in button. Zero demo profile buttons. Zero emojis.
"""

import streamlit as st
from frontend.utils import login_user

def render_login_page():
    # Centered Header Branding
    st.markdown("""
    <div style="text-align: center; margin-top: 40px; margin-bottom: 24px;">
        <div style="font-size: 34px; font-weight: 800; color: #0F172A; letter-spacing: -0.5px; margin: 0;">LANDGUARD AI</div>
        <div style="font-size: 15px; font-weight: 700; color: #0284C7; margin-top: 4px;">Predict Before It Delays.</div>
        <div style="font-size: 13px; color: #64748B; margin-top: 4px;">Predictive Analytics System for Early Detection of Land Acquisition Delays</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:
        st.markdown("<h4 style='color:#0F172A; font-size:16px; font-weight:800; margin-bottom:4px; text-transform:uppercase; letter-spacing:0.8px;'>AUTHORIZED SYSTEM ACCESS</h4>", unsafe_allow_html=True)
        st.caption("Sign in to access LANDGUARD AI decision-support services.")

        username_input = st.text_input("Username", placeholder="Enter your authorized username", key="input_uname")
        password_input = st.text_input("Password", type="password", placeholder="Enter your password", key="input_pwd")

        st.markdown("<br/>", unsafe_allow_html=True)
        if st.button("SIGN IN", type="primary", use_container_width=True, key="btn_login_submit"):
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
        <div style="text-align: center; margin-top: 36px; font-size: 11px; color: #94A3B8;">
            Authorized users only | LANDGUARD AI &bull; Predictive Decision Support<br/>
            <span style="color:#16A34A; font-weight:600;">System Status: Operational</span>
        </div>
        """, unsafe_allow_html=True)
