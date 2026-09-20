"""
Exact Reference Design Theme & CSS Engine for VISTRA.
Forces clean white elevated card elements (#FFFFFF), forest green brand accent (#1E4D2B / #166534), dark navy sidebar (#0B132B), and fixed floating circular AI bot button.
"""

import streamlit as st

def apply_custom_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    .stApp {
        background-color: #F8FAFC;
    }

    /* Top Command Header */
    .header-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 0 16px 0;
        border-bottom: 1px solid #E2E8F0;
        margin-bottom: 20px;
        background: #FFFFFF;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }

    /* Crisp White KPI & Container Cards */
    .kpi-card-exact {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        padding: 18px !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04) !important;
        height: 100% !important;
        position: relative !important;
    }

    .kpi-header-row {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;
    }

    .kpi-icon-wrapper {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 15px;
    }

    .kpi-label-exact {
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.6px;
        text-transform: uppercase;
    }

    .kpi-val-exact {
        font-size: 26px;
        font-weight: 800;
        color: #0F172A !important;
        line-height: 1.1;
        margin: 4px 0;
    }

    .kpi-sub-exact {
        font-size: 11px;
        color: #64748B !important;
        margin-bottom: 8px;
    }

    .kpi-trend-badge {
        font-size: 11px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }

    .trend-up-green { color: #16A34A; }
    .trend-up-red { color: #DC2626; }
    .trend-up-orange { color: #EA580C; }
    .trend-down-green { color: #16A34A; }

    .chart-title-exact {
        font-size: 12px;
        font-weight: 800;
        color: #0F172A !important;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* White Background Content Rectangles & Expanders */
    .stExpander {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
    }

    /* Priority Alerts Rows */
    .alert-row-item {
        padding: 10px 14px;
        border-radius: 8px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 12px;
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
    }

    .alert-bg-critical { background-color: #FEF2F2 !important; border-left: 4px solid #DC2626 !important; }
    .alert-bg-high { background-color: #FFF7ED !important; border-left: 4px solid #EA580C !important; }

    /* Deep Slate Navy Sidebar (#0B132B / #0F172A) */
    section[data-testid="stSidebar"], div[data-testid="stSidebar"] {
        background-color: #0B132B !important;
        border-right: 1px solid #1E293B;
    }

    section[data-testid="stSidebar"] *, div[data-testid="stSidebar"] * {
        color: #F8FAFC !important;
        opacity: 1 !important;
    }

    .sidebar-section-label {
        font-size: 10px;
        font-weight: 700;
        color: #64748B !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 10px 12px 4px 12px;
    }

    /* VISTRA Forest Green (#166534 / #1E4D2B) for Active Navigation Buttons */
    section[data-testid="stSidebar"] .stButton > button[kind="primary"],
    div[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background-color: #166534 !important;
        background-image: linear-gradient(135deg, #1E4D2B 0%, #15803D 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 700 !important;
        text-align: left !important;
        font-size: 13px !important;
        padding: 8px 14px !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 8px rgba(22, 101, 52, 0.4) !important;
    }

    section[data-testid="stSidebar"] .stButton > button[kind="secondary"],
    div[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
        background-color: transparent !important;
        background-image: none !important;
        color: #E2E8F0 !important;
        border: none !important;
        text-align: left !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        padding: 8px 12px !important;
        border-radius: 6px !important;
        opacity: 1 !important;
    }

    section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover,
    div[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
    }

    /* Small Circular Floating AI Assistant Button (Forest Green Accent) */
    div[data-testid="stPopover"] {
        position: fixed !important;
        right: 24px !important;
        bottom: 24px !important;
        z-index: 999999 !important;
        width: 56px !important;
        height: 56px !important;
    }

    div[data-testid="stPopover"] > button {
        background-color: #166534 !important;
        background-image: linear-gradient(135deg, #1E4D2B 0%, #15803D 100%) !important;
        color: #FFFFFF !important;
        border-radius: 50% !important;
        width: 56px !important;
        height: 56px !important;
        min-width: 56px !important;
        max-width: 56px !important;
        min-height: 56px !important;
        max-height: 56px !important;
        padding: 0 !important;
        font-weight: 800 !important;
        font-size: 20px !important;
        box-shadow: 0 4px 18px rgba(22, 101, 52, 0.6) !important;
        border: 2px solid #FFFFFF !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.2s ease !important;
        overflow: hidden !important;
    }

    div[data-testid="stPopover"] > button:hover {
        background-color: #14532D !important;
        transform: scale(1.08) !important;
        box-shadow: 0 6px 22px rgba(22, 101, 52, 0.8) !important;
    }

    div[data-testid="stPopover"] > button p {
        font-size: 20px !important;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1 !important;
    }

    .dataframe {
        font-size: 12px !important;
        border: 1px solid #E2E8F0 !important;
        background-color: #FFFFFF !important;
    }
    </style>
    """, unsafe_allow_html=True)

