"""
Interactive Folium GIS Map Page for VISTRA.
Features cluster markers and HeatMap risk density overlays.
"""

import streamlit as st
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import pandas as pd

from frontend.utils import fetch_filtered_projects
from backend.database import execute_query
from backend.permissions import build_scope_filter
from utils.geo_data import GEO_REFERENCE, LIFECYCLE_STAGES

def render_gis_map_page(user: dict):
    st.markdown("## GIS Geographic Risk Map")

    c1, c2, c3 = st.columns(3)
    with c1:
        risk_filter = st.selectbox("Filter Risk Category", ["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"], key="gis_risk_sel")
    with c2:
        stage_filter = st.selectbox("Filter Acquisition Stage", ["ALL"] + LIFECYCLE_STAGES, key="gis_stg_sel")
    with c3:
        map_layer_type = st.radio("Map Layer View", ["Marker Clusters", "Risk Density HeatMap"], horizontal=True, key="gis_layer_radio")

    scope_sql, params = build_scope_filter(user, table_prefix="p")
    conditions = [f"({scope_sql})"]
    query_params = list(params)

    if risk_filter != "ALL":
        conditions.append("rh.risk_category = ?")
        query_params.append(risk_filter)

    if stage_filter != "ALL":
        conditions.append("p.current_stage = ?")
        query_params.append(stage_filter)

    where_clause = " AND ".join(conditions)

    sql = f"""
    SELECT p.project_id, p.project_name, p.project_type, p.state_name, p.district_name, p.current_stage,
           g.latitude, g.longitude,
           rh.risk_category, rh.risk_score, rh.expected_delay_days, rh.delay_probability
    FROM projects p
    JOIN project_geospatial g ON p.project_id = g.project_id
    LEFT JOIN risk_history rh ON p.project_id = rh.project_id
    WHERE {where_clause}
    LIMIT 400
    """
    rows = execute_query(sql, tuple(query_params))

    if not rows:
        st.info("No projects found matching the map filters within your authorized scope.")
        return

    st.caption(f"Displaying **{len(rows)}** project coordinates. Markers reflect risk severity.")

    lats = [r["latitude"] for r in rows if r["latitude"]]
    lons = [r["longitude"] for r in rows if r["longitude"]]

    avg_lat = sum(lats) / len(lats) if lats else 20.5937
    avg_lon = sum(lons) / len(lons) if lons else 78.9629

    zoom_level = 5 if user.get("scope_type") == "NATIONAL" else (7 if user.get("scope_type") == "STATE" else 10)

    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=zoom_level, tiles="OpenStreetMap")

    if map_layer_type == "Risk Density HeatMap":
        # HeatMap data points: [lat, lon, weight]
        heat_data = [[r["latitude"], r["longitude"], (r["risk_score"] or 10.0) / 100.0] for r in rows if r["latitude"] and r["longitude"]]
        HeatMap(heat_data, radius=18, blur=12, max_zoom=10).add_to(m)
    else:
        color_map = {
            "CRITICAL": "red",
            "HIGH": "orange",
            "MEDIUM": "darkblue",
            "LOW": "green"
        }

        for r in rows:
            cat = r["risk_category"] or "LOW"
            marker_color = color_map.get(cat, "blue")

            popup_html = f"""
            <div style="font-family:sans-serif; width:220px;">
                <b style="color:#0F172A;">{r['project_id']}</b><br/>
                <b>{r['project_name']}</b><br/>
                <span style="font-size:11px; color:#4B5563;">{r['district_name']}, {r['state_name']}</span><br/>
                <hr style="margin:4px 0;"/>
                Risk Level: <b>{cat} ({r['risk_score']}%)</b><br/>
                Stage: {r['current_stage']}<br/>
                Expected Delay: <b>{r['expected_delay_days']} Days</b>
            </div>
            """

            folium.CircleMarker(
                location=[r["latitude"], r["longitude"]],
                radius=7,
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"{r['project_id']} - {r['project_name']} ({cat})",
                color=marker_color,
                fill=True,
                fill_color=marker_color,
                fill_opacity=0.8
            ).add_to(m)

    st_folium(m, width=1000, height=520)
