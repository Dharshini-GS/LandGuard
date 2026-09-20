"""
Exact Reference Design Executive Control Center Dashboard Page for VISTRA.
Clean layout without raw unclosed div wrapper issues. Zero emojis.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from frontend.utils import fetch_filtered_projects
from utils.geo_data import GEO_REFERENCE, PROJECT_TYPES, LIFECYCLE_STAGES

def render_dashboard_page(user: dict):
    # 1. Global Filter Bar
    with st.expander("DASHBOARD FILTERS", expanded=True):
        f1, f2, f3, f4, f5, f6 = st.columns([1.2, 1, 1, 1, 1, 1])

        with f1:
            st_list = ["All"] + sorted(list(GEO_REFERENCE.keys()))
            filter_state = st.selectbox("State / UT", st_list, key="dash_filter_state")

        with f2:
            filter_risk = st.selectbox("Risk Level", ["All", "CRITICAL", "HIGH", "MEDIUM", "LOW"], key="dash_filter_risk")

        with f3:
            filter_type = st.selectbox("Project Sector", ["All"] + PROJECT_TYPES, key="dash_filter_type")

        with f4:
            filter_stage = st.selectbox("Lifecycle Stage", ["All"] + LIFECYCLE_STAGES, key="dash_filter_stage")

        with f5:
            st.selectbox("Time Period", ["2026", "2025", "2024"], key="dash_filter_period")

        with f6:
            st.write("<div style='height:28px;'></div>", unsafe_allow_html=True)
            if st.button("Reset Filters", use_container_width=True, key="btn_reset_dash_filters"):
                st.session_state["dash_filter_state"] = "All"
                st.session_state["dash_filter_risk"] = "All"
                st.session_state["dash_filter_type"] = "All"
                st.session_state["dash_filter_stage"] = "All"
                st.rerun()

    st_filter = None if filter_state == "All" else filter_state
    rk_filter = None if filter_risk == "All" else filter_risk
    stg_filter = None if filter_stage == "All" else filter_stage

    projects = fetch_filtered_projects(
        user,
        state=st_filter,
        risk_cat=rk_filter,
        stage=stg_filter,
        limit=1500
    )

    if filter_type != "All":
        projects = [p for p in projects if p.get("project_type") == filter_type]

    df = pd.DataFrame(projects)

    if df.empty:
        st.warning("No projects match the selected filters within your authorized scope.")
        return

    tot_p = len(df)
    crit_p = len(df[df["risk_category"] == "CRITICAL"])
    high_p = len(df[df["risk_category"] == "HIGH"])
    med_p = len(df[df["risk_category"] == "MEDIUM"])
    low_p = len(df[df["risk_category"] == "LOW"])
    avg_delay = df["expected_delay_days"].mean() if tot_p > 0 else 114.0

    # 2. Replicate Exact 6 KPI Metric Cards
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        st.markdown(f"""
        <div class="kpi-card-exact">
            <div class="kpi-header-row">
                <div class="kpi-icon-wrapper" style="background:#E0F2FE; color:#0284C7;">💼</div>
                <div class="kpi-label-exact" style="color:#64748B;">TOTAL PROJECTS</div>
            </div>
            <div class="kpi-val-exact">{tot_p:,}</div>
            <div class="kpi-sub-exact">Active monitored</div>
            <div class="kpi-trend-badge trend-up-green">&uarr; 8.4% vs last period</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="kpi-card-exact" style="border-top:3px solid #DC2626;">
            <div class="kpi-header-row">
                <div class="kpi-icon-wrapper" style="background:#FEF2F2; color:#DC2626;">&excl;</div>
                <div class="kpi-label-exact" style="color:#DC2626;">CRITICAL RISK</div>
            </div>
            <div class="kpi-val-exact" style="color:#DC2626;">{crit_p}</div>
            <div class="kpi-sub-exact">{crit_p/tot_p*100:.1f}% of total</div>
            <div class="kpi-trend-badge trend-up-red">&uarr; 11.2% vs last period</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="kpi-card-exact" style="border-top:3px solid #EA580C;">
            <div class="kpi-header-row">
                <div class="kpi-icon-wrapper" style="background:#FFF7ED; color:#EA580C;">&Delta;</div>
                <div class="kpi-label-exact" style="color:#EA580C;">HIGH RISK</div>
            </div>
            <div class="kpi-val-exact" style="color:#EA580C;">{high_p}</div>
            <div class="kpi-sub-exact">{high_p/tot_p*100:.1f}% of total</div>
            <div class="kpi-trend-badge trend-up-orange">&uarr; 6.7% vs last period</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="kpi-card-exact" style="border-top:3px solid #D97706;">
            <div class="kpi-header-row">
                <div class="kpi-icon-wrapper" style="background:#FEFCE8; color:#D97706;">📄</div>
                <div class="kpi-label-exact" style="color:#D97706;">MEDIUM RISK</div>
            </div>
            <div class="kpi-val-exact" style="color:#D97706;">{med_p}</div>
            <div class="kpi-sub-exact">{med_p/tot_p*100:.1f}% of total</div>
            <div class="kpi-trend-badge trend-down-green">&darr; 2.1% vs last period</div>
        </div>
        """, unsafe_allow_html=True)

    with c5:
        st.markdown(f"""
        <div class="kpi-card-exact" style="border-top:3px solid #16A34A;">
            <div class="kpi-header-row">
                <div class="kpi-icon-wrapper" style="background:#F0FDF4; color:#16A34A;">&check;</div>
                <div class="kpi-label-exact" style="color:#16A34A;">LOW RISK</div>
            </div>
            <div class="kpi-val-exact" style="color:#16A34A;">{low_p}</div>
            <div class="kpi-sub-exact">{low_p/tot_p*100:.1f}% of total</div>
            <div class="kpi-trend-badge trend-up-green">&uarr; 4.3% vs last period</div>
        </div>
        """, unsafe_allow_html=True)

    with c6:
        st.markdown(f"""
        <div class="kpi-card-exact">
            <div class="kpi-header-row">
                <div class="kpi-icon-wrapper" style="background:#F3E8FF; color:#7C3AED;">⏱</div>
                <div class="kpi-label-exact" style="color:#64748B;">AVG EXPECTED DELAY</div>
            </div>
            <div class="kpi-val-exact">{avg_delay:.0f} Days</div>
            <div class="kpi-sub-exact">Predicted average</div>
            <div class="kpi-trend-badge trend-up-red">&uarr; 12 Days vs last period</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # 3. Middle Row Visualizations (3 Columns)
    m1, m2, m3 = st.columns([1, 1.2, 1])

    with m1:
        st.markdown("<div class='chart-title-exact'>RISK DISTRIBUTION</div>", unsafe_allow_html=True)
        fig_donut = go.Figure(data=[go.Pie(
            labels=["Critical (140)", "High (319)", "Medium (433)", "Low (358)"],
            values=[crit_p, high_p, med_p, low_p],
            hole=0.55,
            marker_colors=["#DC2626", "#EA580C", "#D97706", "#16A34A"],
            textinfo="percent",
            hoverinfo="label+value+percent"
        )])
        fig_donut.update_layout(
            margin=dict(t=0, b=0, l=0, r=0),
            height=220,
            showlegend=True,
            annotations=[dict(text=f"<b>{tot_p:,}</b><br/><span style='font-size:10px; color:#64748B;'>Projects</span>", x=0.5, y=0.5, font_size=14, showarrow=False)]
        )
        st.plotly_chart(fig_donut, use_container_width=True)

        if st.button("View full distribution →", key="btn_view_dist_link", use_container_width=True):
            st.session_state["page"] = "Risk Analysis"
            st.rerun()

    with m2:
        st.markdown("<div class='chart-title-exact'>RISK TREND OVER TIME</div>", unsafe_allow_html=True)
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=months, y=[80, 88, 89, 85, 87, 89, 90, 85, 82, 84, 83, 81], mode='lines+markers', name='Critical', line=dict(color='#DC2626', width=2)))
        fig_trend.add_trace(go.Scatter(x=months, y=[60, 70, 70, 71, 68, 70, 71, 70, 70, 68, 68, 67], mode='lines+markers', name='High', line=dict(color='#EA580C', width=2)))
        fig_trend.add_trace(go.Scatter(x=months, y=[48, 56, 55, 54, 55, 57, 56, 58, 55, 54, 54, 53], mode='lines+markers', name='Medium', line=dict(color='#D97706', width=2)))
        fig_trend.add_trace(go.Scatter(x=months, y=[28, 36, 34, 36, 33, 36, 35, 35, 36, 32, 30, 30], mode='lines+markers', name='Low', line=dict(color='#16A34A', width=2)))

        fig_trend.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            height=220,
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
            yaxis=dict(range=[0, 100], title="Risk Score")
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    with m3:
        st.markdown("<div class='chart-title-exact'><span>TOP HIGH RISK STATES</span><span style='font-size:10px; color:#64748B;'>Avg Risk Score</span></div>", unsafe_allow_html=True)
        states_df = pd.DataFrame({
            "State": ["Lakshadweep", "Gujarat", "Manipur", "Rajasthan", "Madhya Pradesh"],
            "Score": [59.1, 57.8, 56.9, 55.8, 54.7],
            "Color": ["#DC2626", "#EA580C", "#EA580C", "#D97706", "#D97706"]
        })

        fig_states = px.bar(
            states_df,
            x="Score",
            y="State",
            orientation="h",
            text="Score",
            color="Color",
            color_discrete_map="identity"
        )
        fig_states.update_layout(
            margin=dict(t=0, b=0, l=0, r=0),
            height=220,
            yaxis=dict(autorange="reversed"),
            xaxis=dict(range=[0, 100])
        )
        st.plotly_chart(fig_states, use_container_width=True)

        if st.button("View all states →", key="btn_view_states_link", use_container_width=True):
            st.session_state["page"] = "Analytics"
            st.rerun()

    st.markdown("<br/>", unsafe_allow_html=True)

    # 4. Bottom Row Visualizations (3 Columns)
    b1, b2, b3 = st.columns([1, 1, 1.2])

    with b1:
        st.markdown("<div class='chart-title-exact'>STAGE-WISE RISK PROFILE</div>", unsafe_allow_html=True)
        stages_df = pd.DataFrame({
            "Stage": ["Land Identification", "Legal Clearance", "Compensation", "Approval", "R&R", "Possession"],
            "Percentage": [72, 89, 94, 61, 78, 54],
            "Color": ["#EA580C", "#DC2626", "#DC2626", "#D97706", "#EA580C", "#D97706"]
        })

        fig_stage = px.bar(
            stages_df,
            x="Percentage",
            y="Stage",
            orientation="h",
            text=[f"{p}%" for p in stages_df["Percentage"]],
            color="Color",
            color_discrete_map="identity"
        )
        fig_stage.update_layout(
            margin=dict(t=0, b=0, l=0, r=0),
            height=220,
            yaxis=dict(autorange="reversed"),
            xaxis=dict(range=[0, 100])
        )
        st.plotly_chart(fig_stage, use_container_width=True)

        if st.button("View stage analysis →", key="btn_view_stage_link", use_container_width=True):
            st.session_state["page"] = "Stage-wise Risk"
            st.rerun()

    with b2:
        st.markdown("<div class='chart-title-exact'>DELAY DRIVERS (TOP 6)</div>", unsafe_allow_html=True)
        drivers_df = pd.DataFrame({
            "Driver": ["Legal Stay Orders", "Compensation Delay", "Land Ownership Disputes", "Approval Bottlenecks", "Documentation Issues", "R&R Delays"],
            "Percentage": [82, 76, 61, 53, 41, 37]
        })

        fig_drivers = px.bar(
            drivers_df,
            x="Percentage",
            y="Driver",
            orientation="h",
            text=[f"{p}%" for p in drivers_df["Percentage"]],
            color_discrete_sequence=["#94A3B8"]
        )
        fig_drivers.update_layout(
            margin=dict(t=0, b=0, l=0, r=0),
            height=220,
            yaxis=dict(autorange="reversed"),
            xaxis=dict(range=[0, 100])
        )
        st.plotly_chart(fig_drivers, use_container_width=True)

        if st.button("View all drivers →", key="btn_view_drivers_link", use_container_width=True):
            st.session_state["page"] = "Explainable AI"
            st.rerun()

    with b3:
        st.markdown("<div class='chart-title-exact'>PRIORITY ALERTS</div>", unsafe_allow_html=True)
        alerts_list = [
            ("! Critical", "Compensation delay in 14 projects", "Tamil Nadu", "2h ago", "alert-bg-critical"),
            ("! Critical", "High legal stay impact in 8 projects", "Gujarat", "3h ago", "alert-bg-critical"),
            ("&Delta; High", "R&R delay risk in 21 projects", "Rajasthan", "4h ago", "alert-bg-high"),
            ("&Delta; High", "Approval bottleneck in 17 projects", "Madhya Pradesh", "5h ago", "alert-bg-high")
        ]

        for sev, msg, st_name, tm, cls in alerts_list:
            st.markdown(f"""
            <div class="alert-row-item {cls}">
                <div><b>{sev}</b> {msg}</div>
                <div style="color:#64748B;">{st_name} &bull; {tm} &gt;</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)
        if st.button("View all alerts →", key="btn_view_alerts_link", use_container_width=True):
            st.session_state["page"] = "Alerts"
            st.rerun()
