"""
ReportLab PDF Generation Service for VISTRA.
Creates executive project risk assessment PDF reports with clean styling.
"""

import sys
import uuid
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from utils.config import REPORTS_DIR
from backend.services.ml_service import ml_service_instance
from backend.database import execute_query_one, execute_query
from utils.logger import get_logger

logger = get_logger("PDFService")

def generate_project_pdf_report(project_id: str) -> Path:
    report_id = f"RPT-{uuid.uuid4().hex[:8].upper()}"
    filepath = REPORTS_DIR / f"{project_id}_risk_report.pdf"

    # Fetch project detail & ML assessment
    query = """
    SELECT 
        p.project_id, p.project_name, p.project_type, p.state_name, p.district_name,
        p.land_area_acres, p.affected_families, p.landowners_count, p.current_stage,
        c.disbursement_percentage AS comp_pct, c.beneficiaries_paid, c.beneficiaries_total,
        l.total_cases, l.pending_cases, l.stay_orders_count,
        d.title_clearance_percentage AS doc_pct,
        a.approval_type, a.status AS approval_status, a.delay_days AS approval_delay,
        r.site_readiness_percentage AS rr_pct,
        s.stakeholder_response_index AS stk_idx,
        adm.bottleneck_score
    FROM projects p
    LEFT JOIN compensation c ON p.project_id = c.project_id
    LEFT JOIN legal_disputes l ON p.project_id = l.project_id
    LEFT JOIN documentation d ON p.project_id = d.project_id
    LEFT JOIN approvals a ON p.project_id = a.project_id
    LEFT JOIN rehabilitation_rr r ON p.project_id = r.project_id
    LEFT JOIN stakeholders s ON p.project_id = s.project_id
    LEFT JOIN administrative_performance adm ON p.project_id = adm.project_id
    WHERE p.project_id = ?
    """
    proj = execute_query_one(query, (project_id,))
    if not proj:
        raise ValueError(f"Project '{project_id}' not found.")

    risk = ml_service_instance.predict_risk(project_id)
    shap_info = ml_service_instance.explain_shap(project_id)

    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=12
    )
    section_heading = ParagraphStyle(
        'SecHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        textColor=colors.HexColor('#0284C7'),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155')
    )

    story = []

    # Title & Metadata Header
    story.append(Paragraph("VISTRA &mdash; Predictive Risk Assessment Report", title_style))
    story.append(Paragraph(f"Report ID: {report_id} | Project ID: {project_id} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284C7'), spaceAfter=10))

    # 1. Project Identification Table
    story.append(Paragraph("1. Project Summary Information", section_heading))
    summary_data = [
        ["Project Name:", proj.get("project_name", "N/A"), "Sector:", proj.get("project_type", "N/A")],
        ["State / UT:", proj.get("state_name", "N/A"), "District:", proj.get("district_name", "N/A")],
        ["Current Stage:", proj.get("current_stage", "N/A"), "Land Area (Acres):", f"{proj.get('land_area_acres', 0):,.1f}"],
        ["Affected Families:", f"{proj.get('affected_families', 0):,}", "Landowners Count:", f"{proj.get('landowners_count', 0):,}"]
    ]
    t_summary = Table(summary_data, colWidths=[110, 160, 110, 160])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (2,0), (2,-1), colors.HexColor('#F8FAFC')),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 10))

    # 2. Predictive Risk Assessment Box
    story.append(Paragraph("2. ML Delay Risk Assessment", section_heading))
    cat = risk["risk_category"]
    cat_color = "#DC2626" if cat == "CRITICAL" else "#EA580C" if cat == "HIGH" else "#D97706" if cat == "MEDIUM" else "#16A34A"

    risk_data = [
        ["Predictive Risk Score", "Risk Category", "Predicted Completion Delay", "Delay Probability"],
        [f"{risk['risk_score']:.1f} / 100", cat, f"{risk['expected_delay_days']} Days", f"{risk['delay_probability']*100:.1f}%"]
    ]
    t_risk = Table(risk_data, colWidths=[135, 135, 135, 135])
    t_risk.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TEXTCOLOR', (1,1), (1,1), colors.HexColor(cat_color)),
        ('FONTNAME', (0,1), (-1,1), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_risk)
    story.append(Spacer(1, 10))

    # 3. Sub-System Status Overview
    story.append(Paragraph("3. Acquisition Sub-System Metrics", section_heading))
    sub_data = [
        ["Sub-System", "Key Operational Metric", "Status / Performance"],
        ["Compensation Processing", "Disbursement Progress", f"{proj.get('comp_pct', 0.0):.1f}% Completed"],
        ["Legal Disputes", "Pending Court Cases / Stay Orders", f"{proj.get('pending_cases', 0)} Pending ({proj.get('stay_orders_count', 0)} Stay Orders)"],
        ["Title Clearance Documentation", "Clearance Percentage", f"{proj.get('doc_pct', 0.0):.1f}% Cleared"],
        ["Rehabilitation & Resettlement", "Site Readiness Index", f"{proj.get('rr_pct', 0.0):.1f}% Ready"]
    ]
    t_sub = Table(sub_data, colWidths=[150, 220, 170])
    t_sub.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_sub)
    story.append(Spacer(1, 10))

    # 4. Explainable AI SHAP Drivers
    story.append(Paragraph("4. Explainable AI (SHAP) Factor Attribution", section_heading))
    shap_rows = [["Feature Name", "SHAP Impact Value", "Effect", "Diagnostic Summary"]]
    for f in shap_info["top_contributors"][:5]:
        shap_rows.append([
            f["human_label"],
            f"{f['shap_value']:+.4f}",
            "Increases Delay" if f["shap_value"] > 0 else "Reduces Delay",
            f["explanation"]
        ])
    t_shap = Table(shap_rows, colWidths=[140, 90, 90, 220])
    t_shap.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#334155')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_shap)
    story.append(Spacer(1, 12))

    # 5. Priority Recommendations
    story.append(Paragraph("5. Recommended Tactical Interventions", section_heading))
    recs = [
        "1. Expedite pending compensation disbursement to beneficiaries to minimize landowner friction.",
        "2. Establish fast-track legal resolution tribunal for pending district and high court stay orders.",
        "3. Prioritize land title clearance documentation and revenue office verification.",
        "4. Escalate pending environmental/forest clearances with nodal state authorities."
    ]
    for r in recs:
        story.append(Paragraph(r, body_style))
        story.append(Spacer(1, 3))

    doc.build(story)
    logger.info(f"Generated PDF report for project {project_id} at {filepath}")
    return filepath
