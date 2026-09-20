"""
Scope-Aware AI Assistant Interface Page for VISTRA.
Provides conversational intelligence strictly bounded to user scope.
"""

import streamlit as st
import pandas as pd

from backend.permissions import build_scope_filter
from backend.database import execute_query
from frontend.utils import get_scope_label
from backend.services.audit_service import log_action

def render_ai_assistant_page(user: dict):
    st.markdown("## 🤖 AI Assistant — Scope-Aware Decision Support")

    scope_label = get_scope_label(user)
    st.caption(f"🔒 Active Query Scope: **{scope_label}**")

    st.markdown("#### Suggested Queries:")
    c1, c2, c3 = st.columns(3)

    query_input = ""
    with c1:
        if st.button("🚨 Projects needing immediate attention?", use_container_width=True, key="ai_suggest_1"):
            query_input = "Which projects need immediate attention?"
        if st.button("⚡ Highest risk projects?", use_container_width=True, key="ai_suggest_2"):
            query_input = "What is causing the highest risk?"

    with c2:
        if st.button("🔥 Show critical projects", use_container_width=True, key="ai_suggest_3"):
            query_input = "Show critical projects"
        if st.button("🛠️ What actions should be taken?", use_container_width=True, key="ai_suggest_4"):
            query_input = "What action should be taken?"

    with c3:
        if st.button("⚖️ High legal dispute cases?", use_container_width=True, key="ai_suggest_5"):
            query_input = "Show projects with high legal disputes"

    user_query = st.text_input("Ask VISTRA Assistant a question:", value=query_input, placeholder="e.g. Which projects need immediate attention?", key="ai_query_input_text")

    if user_query:
        _process_ai_query(user, user_query)

def _process_ai_query(user: dict, query: str):
    scope_sql, params = build_scope_filter(user, table_prefix="p")
    q_lower = query.lower()

    sql = f"""
    SELECT p.project_id, p.project_name, p.state_name, p.district_name, p.current_stage, p.project_type,
           rh.risk_category, rh.risk_score, rh.expected_delay_days, rh.delay_probability
    FROM projects p
    LEFT JOIN risk_history rh ON p.project_id = rh.project_id
    WHERE ({scope_sql})
    ORDER BY rh.risk_score DESC
    LIMIT 5
    """
    top_projects = execute_query(sql, tuple(params))

    scope_label = get_scope_label(user)

    st.markdown("---")
    st.markdown("### 💬 Assistant Diagnostic Response")

    if not top_projects:
        st.warning(f"No project data found within your authorized scope ({scope_label}).")
        return

    if "critical" in q_lower or "immediate" in q_lower or "attention" in q_lower:
        crit_list = [p for p in top_projects if p["risk_category"] == "CRITICAL"]
        if crit_list:
            names = ", ".join([f"**{p['project_id']}** ({p['project_name']} - {p['risk_score']}%)" for p in crit_list[:3]])
            st.write(f"Within **{scope_label}**, there are **{len(crit_list)} CRITICAL-risk projects** requiring immediate intervention: {names}. Primary bottlenecks center around legal stay orders and compensation disbursement delays.")
        else:
            st.write(f"Within **{scope_label}**, no project is currently in the CRITICAL category. The highest risk project is **{top_projects[0]['project_id']}** at {top_projects[0]['risk_score']}% risk.")

    elif "highest risk" in q_lower or "worst" in q_lower:
        p1 = top_projects[0]
        st.write(f"The highest-risk project under **{scope_label}** is **{p1['project_id']}** ({p1['project_name']}) in {p1['district_name']}, {p1['state_name']}. It has a predicted delay probability of **{p1['delay_probability']*100:.1f}%** ({p1['risk_category']}) with an estimated completion delay of **{p1['expected_delay_days']} days**.")

    elif "action" in q_lower or "recommend" in q_lower:
        p1 = top_projects[0]
        st.write(f"For top risk projects under **{scope_label}** (such as **{p1['project_id']}**), key recommended actions are: 1) Accelerate direct benefit compensation payments, 2) Fast-track pending district court stay order resolutions, and 3) Escalate clearance applications to nodal officers.")

    else:
        st.write(f"Analyzed records for **{scope_label}**. Found {len(top_projects)} high-priority projects. Top project **{top_projects[0]['project_id']}** ({top_projects[0]['project_name']}) stands at {top_projects[0]['risk_score']}% risk ({top_projects[0]['risk_category']}).")

    st.markdown("#### Related Authorized Projects:")
    df_rel = pd.DataFrame(top_projects)
    st.dataframe(
        df_rel[["project_id", "project_name", "state_name", "district_name", "current_stage", "risk_category", "risk_score", "expected_delay_days"]],
        use_container_width=True,
        hide_index=True
    )

    log_action(user, "AI_ASSISTANT_QUERY", details=f"Query: '{query}' | Scope: {scope_label}")
