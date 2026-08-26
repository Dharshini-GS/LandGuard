"""
Data Generator for LANDGUARD AI (SIH26017 Prototype).
Generates ~1,300 realistic synthetic project records across all 28 Indian States and 8 Union Territories.
Applies controlled correlations and noise for realistic risk distribution.
Outputs 14 CSV files to data/ directory.
"""

import sys
import os
from pathlib import Path
import random
import csv
import math
from datetime import datetime, timedelta
# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from passlib.hash import pbkdf2_sha256
from utils.geo_data import GEO_REFERENCE, PROJECT_TYPES, LIFECYCLE_STAGES
from utils.config import DATA_DIR
from utils.logger import get_logger

logger = get_logger("DataGenerator")

def hash_password(password: str) -> str:
    return pbkdf2_sha256.hash(password)

def random_date(start_year=2021, end_year=2024):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    return (start + timedelta(days=random_days)).strftime("%Y-%m-%d")

def generate_dataset():
    random.seed(42)  # Reproducible synthetic generation
    logger.info("Starting synthetic dataset generation...")

    # Pre-hash common passwords
    pass_hash_admin = hash_password("admin123")
    pass_hash_state = hash_password("state123")
    pass_hash_district = hash_password("district123")
    pass_hash_pm = hash_password("pm123")
    pass_hash_analyst = hash_password("analyst123")

    projects = []
    land_parcels = []
    timeline_records = []
    compensation_records = []
    legal_records = []
    approval_records = []
    documentation_records = []
    rr_records = []
    stakeholder_records = []
    admin_records = []
    geospatial_records = []
    outcome_records = []
    risk_history_records = []

    # Map of projects assigned per district / state for user scoping
    state_district_projects = {}

    project_counter = 1

    # Force inclusion of demo project LG-TN-0042 first
    demo_proj_id = "LG-TN-0042"
    demo_state_code = "TN"
    demo_state_name = GEO_REFERENCE["TN"]["name"]
    demo_district = GEO_REFERENCE["TN"]["districts"][1]  # Coimbatore
    demo_district_code = demo_district["code"]
    demo_district_name = demo_district["name"]

    projects.append({
        "project_id": demo_proj_id,
        "project_name": "Highway Expansion - Coimbatore Section",
        "project_type": "Highway Expansion",
        "state_code": demo_state_code,
        "state_name": demo_state_name,
        "district_code": demo_district_code,
        "district_name": demo_district_name,
        "land_area_acres": 800.0,
        "affected_families": 450,
        "landowners_count": 380,
        "budget_inr_cr": 1250.0,
        "current_stage": "Legal Resolution",
        "start_date": "2023-01-15",
        "target_completion_date": "2025-06-30",
        "status": "IN_PROGRESS",
        "created_at": "2023-01-10 10:00:00"
    })

    compensation_records.append({
        "comp_id": "CMP-TN-0042",
        "project_id": demo_proj_id,
        "beneficiaries_total": 450,
        "beneficiaries_paid": 189,  # 42%
        "beneficiaries_pending": 261,
        "amount_sanctioned_cr": 350.0,
        "amount_disbursed_cr": 147.0,
        "disbursement_percentage": 42.0
    })

    legal_records.append({
        "dispute_id": "LGL-TN-0042",
        "project_id": demo_proj_id,
        "total_cases": 18,
        "court_district_cases": 10,
        "court_high_cases": 6,
        "court_supreme_cases": 2,
        "pending_cases": 14,
        "resolved_cases": 4,
        "stay_orders_count": 3
    })

    approval_records.append({
        "approval_id": "APP-TN-0042",
        "project_id": demo_proj_id,
        "approval_type": "Environmental",
        "status": "PENDING",
        "submission_date": "2023-03-01",
        "approval_date": "",
        "delay_days": 90
    })

    documentation_records.append({
        "doc_id": "DOC-TN-0042",
        "project_id": demo_proj_id,
        "total_records": 500,
        "records_verified": 350,
        "records_pending": 150,
        "title_clearance_percentage": 70.0
    })

    rr_records.append({
        "rr_id": "RR-TN-0042",
        "project_id": demo_proj_id,
        "families_eligible": 450,
        "families_rehabilitated": 158, # 35%
        "families_pending": 292,
        "site_readiness_percentage": 35.0,
        "grant_disbursed_cr": 15.5
    })

    stakeholder_records.append({
        "stakeholder_id": "STK-TN-0042",
        "project_id": demo_proj_id,
        "objections_received": 85,
        "objections_resolved": 30,
        "pending_objections": 55,
        "public_hearing_status": "OBJECTED",
        "stakeholder_response_index": 38.0
    })

    admin_records.append({
        "admin_id": "ADM-TN-0042",
        "project_id": demo_proj_id,
        "nodal_officer_assigned": "R. Sundaram (IAS)",
        "dept_workload_score": 8.5,
        "sla_compliance_percentage": 52.0,
        "bottleneck_score": 78.0
    })

    geospatial_records.append({
        "geo_id": "GEO-TN-0042",
        "project_id": demo_proj_id,
        "latitude": demo_district["center"][0] + 0.02,
        "longitude": demo_district["center"][1] + 0.03,
        "boundary_geojson": f'{{"type":"Point","coordinates":[{demo_district["center"][1] + 0.03},{demo_district["center"][0] + 0.02}]}}'
    })

    outcome_records.append({
        "outcome_id": "OUT-TN-0042",
        "project_id": demo_proj_id,
        "delay_flag": 1,
        "delay_days": 320
    })

    risk_history_records.append({
        "history_id": "HIS-TN-0042-1",
        "project_id": demo_proj_id,
        "prediction_date": "2024-01-15",
        "delay_probability": 0.84,
        "risk_score": 84.0,
        "risk_category": "CRITICAL",
        "expected_delay_days": 320,
        "highest_risk_stage": "Legal Resolution",
        "model_version": "v1.0.0"
    })

    state_district_projects.setdefault((demo_state_code, demo_district_code), []).append(demo_proj_id)

    # Generate 1,250 additional synthetic projects across all 36 States/UTs
    all_state_codes = list(GEO_REFERENCE.keys())

    for i in range(2, 1251):
        state_code = all_state_codes[(i - 2) % len(all_state_codes)]
        state_info = GEO_REFERENCE[state_code]
        state_name = state_info["name"]
        district_info = random.choice(state_info["districts"])
        district_code = district_info["code"]
        district_name = district_info["name"]

        proj_type = random.choice(PROJECT_TYPES)
        p_id = f"LG-{state_code}-{i:04d}"

        land_area = round(random.uniform(50.0, 2500.0), 1)
        affected_fam = int(land_area * random.uniform(0.3, 1.2))
        landowners = max(10, int(affected_fam * random.uniform(0.7, 1.1)))
        budget = round(land_area * random.uniform(0.8, 3.5), 1)
        current_stage = random.choice(LIFECYCLE_STAGES)
        start_date = random_date(2021, 2024)

        # Risk archetype generation: High risk (25%), Medium risk (35%), Low risk (30%), Critical (10%)
        risk_archetype = random.choices(
            ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
            weights=[30, 35, 25, 10]
        )[0]

        if risk_archetype == "CRITICAL":
            comp_pct = random.uniform(15.0, 45.0)
            verified_pct = random.uniform(40.0, 75.0)
            pending_cases = random.randint(12, 35)
            stay_orders = random.randint(2, 8)
            rr_pct = random.uniform(10.0, 40.0)
            stk_index = random.uniform(20.0, 45.0)
            bottleneck = random.uniform(70.0, 95.0)
            approval_status = random.choice(["PENDING", "REJECTED"])
            delay_flag = 1
            delay_days = random.randint(250, 600)
            prob = round(random.uniform(0.81, 0.98), 2)
        elif risk_archetype == "HIGH":
            comp_pct = random.uniform(40.0, 65.0)
            verified_pct = random.uniform(60.0, 80.0)
            pending_cases = random.randint(6, 15)
            stay_orders = random.randint(1, 3)
            rr_pct = random.uniform(35.0, 60.0)
            stk_index = random.uniform(45.0, 65.0)
            bottleneck = random.uniform(55.0, 75.0)
            approval_status = random.choice(["PENDING", "APPROVED"])
            delay_flag = 1
            delay_days = random.randint(120, 260)
            prob = round(random.uniform(0.61, 0.80), 2)
        elif risk_archetype == "MEDIUM":
            comp_pct = random.uniform(65.0, 85.0)
            verified_pct = random.uniform(75.0, 90.0)
            pending_cases = random.randint(2, 7)
            stay_orders = random.randint(0, 1)
            rr_pct = random.uniform(60.0, 80.0)
            stk_index = random.uniform(65.0, 80.0)
            bottleneck = random.uniform(30.0, 55.0)
            approval_status = random.choice(["APPROVED", "PENDING"])
            delay_flag = random.choice([0, 1])
            delay_days = random.randint(20, 130) if delay_flag else random.randint(0, 20)
            prob = round(random.uniform(0.31, 0.60), 2)
        else: # LOW
            comp_pct = random.uniform(85.0, 100.0)
            verified_pct = random.uniform(88.0, 100.0)
            pending_cases = random.randint(0, 2)
            stay_orders = 0
            rr_pct = random.uniform(80.0, 100.0)
            stk_index = random.uniform(80.0, 100.0)
            bottleneck = random.uniform(10.0, 35.0)
            approval_status = "APPROVED"
            delay_flag = 0
            delay_days = random.randint(0, 15)
            prob = round(random.uniform(0.05, 0.30), 2)

        projects.append({
            "project_id": p_id,
            "project_name": f"{proj_type} - {district_name} Sector",
            "project_type": proj_type,
            "state_code": state_code,
            "state_name": state_name,
            "district_code": district_code,
            "district_name": district_name,
            "land_area_acres": land_area,
            "affected_families": affected_fam,
            "landowners_count": landowners,
            "budget_inr_cr": budget,
            "current_stage": current_stage,
            "start_date": start_date,
            "target_completion_date": "2026-12-31",
            "status": "IN_PROGRESS",
            "created_at": "2023-01-10 10:00:00"
        })

        paid_fam = int(affected_fam * (comp_pct / 100.0))
        paid_fam = min(paid_fam, affected_fam)
        pending_fam = affected_fam - paid_fam
        sanctioned_amt = round(budget * 0.3, 2)
        disbursed_amt = round(sanctioned_amt * (comp_pct / 100.0), 2)

        compensation_records.append({
            "comp_id": f"CMP-{state_code}-{i:04d}",
            "project_id": p_id,
            "beneficiaries_total": affected_fam,
            "beneficiaries_paid": paid_fam,
            "beneficiaries_pending": pending_fam,
            "amount_sanctioned_cr": sanctioned_amt,
            "amount_disbursed_cr": disbursed_amt,
            "disbursement_percentage": round(comp_pct, 1)
        })

        total_cases = pending_cases + random.randint(1, 10)
        resolved_cases = total_cases - pending_cases

        legal_records.append({
            "dispute_id": f"LGL-{state_code}-{i:04d}",
            "project_id": p_id,
            "total_cases": total_cases,
            "court_district_cases": int(total_cases * 0.6),
            "court_high_cases": int(total_cases * 0.3),
            "court_supreme_cases": total_cases - int(total_cases * 0.6) - int(total_cases * 0.3),
            "pending_cases": pending_cases,
            "resolved_cases": resolved_cases,
            "stay_orders_count": stay_orders
        })

        approval_records.append({
            "approval_id": f"APP-{state_code}-{i:04d}",
            "project_id": p_id,
            "approval_type": random.choice(["Environmental", "Forest", "Revenue", "Wildlife"]),
            "status": approval_status,
            "submission_date": start_date,
            "approval_date": "" if approval_status == "PENDING" else "2024-01-01",
            "delay_days": random.randint(30, 150) if approval_status == "PENDING" else random.randint(0, 15)
        })

        total_docs = landowners + 50
        verified_docs = int(total_docs * (verified_pct / 100.0))
        pending_docs = total_docs - verified_docs

        documentation_records.append({
            "doc_id": f"DOC-{state_code}-{i:04d}",
            "project_id": p_id,
            "total_records": total_docs,
            "records_verified": verified_docs,
            "records_pending": pending_docs,
            "title_clearance_percentage": round(verified_pct, 1)
        })

        rehab_fam = int(affected_fam * (rr_pct / 100.0))
        rehab_fam = min(rehab_fam, affected_fam)
        pending_rr = affected_fam - rehab_fam

        rr_records.append({
            "rr_id": f"RR-{state_code}-{i:04d}",
            "project_id": p_id,
            "families_eligible": affected_fam,
            "families_rehabilitated": rehab_fam,
            "families_pending": pending_rr,
            "site_readiness_percentage": round(rr_pct, 1),
            "grant_disbursed_cr": round(budget * 0.05 * (rr_pct / 100.0), 2)
        })

        objections = random.randint(5, 120)
        obj_resolved = int(objections * (stk_index / 100.0))
        pending_obj = objections - obj_resolved

        stakeholder_records.append({
            "stakeholder_id": f"STK-{state_code}-{i:04d}",
            "project_id": p_id,
            "objections_received": objections,
            "objections_resolved": obj_resolved,
            "pending_objections": pending_obj,
            "public_hearing_status": "HELD" if stk_index > 50 else "PENDING",
            "stakeholder_response_index": round(stk_index, 1)
        })

        admin_records.append({
            "admin_id": f"ADM-{state_code}-{i:04d}",
            "project_id": p_id,
            "nodal_officer_assigned": f"Officer-{state_code}-{i}",
            "dept_workload_score": round(random.uniform(2.0, 9.5), 1),
            "sla_compliance_percentage": round(100.0 - bottleneck * 0.8, 1),
            "bottleneck_score": round(bottleneck, 1)
        })

        # Geo point near district center with minor jitter
        lat = district_info["center"][0] + random.uniform(-0.15, 0.15)
        lon = district_info["center"][1] + random.uniform(-0.15, 0.15)

        geospatial_records.append({
            "geo_id": f"GEO-{state_code}-{i:04d}",
            "project_id": p_id,
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "boundary_geojson": f'{{"type":"Point","coordinates":[{round(lon, 6)},{round(lat, 6)}]}}'
        })

        outcome_records.append({
            "outcome_id": f"OUT-{state_code}-{i:04d}",
            "project_id": p_id,
            "delay_flag": delay_flag,
            "delay_days": delay_days
        })

        risk_score = round(prob * 100.0, 1)
        risk_cat = "CRITICAL" if risk_score > 80 else ("HIGH" if risk_score > 60 else ("MEDIUM" if risk_score > 30 else "LOW"))

        risk_history_records.append({
            "history_id": f"HIS-{state_code}-{i:04d}",
            "project_id": p_id,
            "prediction_date": "2024-02-01",
            "delay_probability": prob,
            "risk_score": risk_score,
            "risk_category": risk_cat,
            "expected_delay_days": delay_days,
            "highest_risk_stage": current_stage,
            "model_version": "v1.0.0"
        })

        state_district_projects.setdefault((state_code, district_code), []).append(p_id)

    # ----------------------------------------------------
    # Generate Synthetic Users across Roles & Scopes
    # ----------------------------------------------------
    users = []

    # 1. ADMIN Users (12)
    for idx in range(1, 13):
        users.append({
            "user_id": f"USR-ADM-{idx:02d}",
            "username": f"admin{idx}" if idx > 1 else "admin",
            "password_hash": pass_hash_admin,
            "full_name": f"National Administrator {idx}",
            "role": "ADMIN",
            "scope_type": "NATIONAL",
            "state_code": "",
            "state_name": "",
            "district_code": "",
            "district_name": "",
            "assigned_project_ids": "",
            "status": "ACTIVE",
            "created_at": "2024-01-01 00:00:00",
            "last_login": "2024-02-25 10:30:00"
        })

    # 2. STATE_OFFICERS (1-2 per State/UT)
    user_counter = 1
    for st_code, st_data in GEO_REFERENCE.items():
        st_name = st_data["name"]
        username = f"state_{st_code.lower()}"
        users.append({
            "user_id": f"USR-STO-{user_counter:03d}",
            "username": username,
            "password_hash": pass_hash_state,
            "full_name": f"State Nodal Officer ({st_name})",
            "role": "STATE_OFFICER",
            "scope_type": "STATE",
            "state_code": st_code,
            "state_name": st_name,
            "district_code": "",
            "district_name": "",
            "assigned_project_ids": "",
            "status": "ACTIVE",
            "created_at": "2024-01-01 00:00:00",
            "last_login": "2024-02-24 14:15:00"
        })
        user_counter += 1

    # 3. DISTRICT_OFFICERS (for districts with projects)
    dist_user_counter = 1
    for (st_code, dist_code), p_ids in state_district_projects.items():
        st_name = GEO_REFERENCE[st_code]["name"]
        dist_name = next(d["name"] for d in GEO_REFERENCE[st_code]["districts"] if d["code"] == dist_code)
        username = f"dist_{dist_code.lower().replace('-', '_')}"
        users.append({
            "user_id": f"USR-DTO-{dist_user_counter:03d}",
            "username": username,
            "password_hash": pass_hash_district,
            "full_name": f"District Collector ({dist_name})",
            "role": "DISTRICT_OFFICER",
            "scope_type": "DISTRICT",
            "state_code": st_code,
            "state_name": st_name,
            "district_code": dist_code,
            "district_name": dist_name,
            "assigned_project_ids": "",
            "status": "ACTIVE",
            "created_at": "2024-01-01 00:00:00",
            "last_login": "2024-02-23 09:00:00"
        })
        dist_user_counter += 1

    # 4. PROJECT_MANAGERS (Assigned to clusters of projects)
    all_proj_ids = [p["project_id"] for p in projects]
    chunk_size = 10
    pm_counter = 1
    for k in range(0, len(all_proj_ids), chunk_size):
        assigned_chunk = all_proj_ids[k:k+chunk_size]
        username = f"pm_{pm_counter}" if pm_counter > 1 else "pm_user"
        # Demo PM specifically gets LG-TN-0042
        if demo_proj_id in assigned_chunk:
            username = "pm_user"

        users.append({
            "user_id": f"USR-PJM-{pm_counter:03d}",
            "username": username,
            "password_hash": pass_hash_pm,
            "full_name": f"Project Manager {pm_counter}",
            "role": "PROJECT_MANAGER",
            "scope_type": "PROJECT",
            "state_code": "",
            "state_name": "",
            "district_code": "",
            "district_name": "",
            "assigned_project_ids": ",".join(assigned_chunk),
            "status": "ACTIVE",
            "created_at": "2024-01-01 00:00:00",
            "last_login": "2024-02-25 11:20:00"
        })
        pm_counter += 1

    # 5. ANALYST Users (15)
    for idx in range(1, 16):
        username = f"analyst{idx}" if idx > 1 else "analyst"
        users.append({
            "user_id": f"USR-ANY-{idx:02d}",
            "username": username,
            "password_hash": pass_hash_analyst,
            "full_name": f"Lead Policy Analyst {idx}",
            "role": "ANALYST",
            "scope_type": "NATIONAL",
            "state_code": "",
            "state_name": "",
            "district_code": "",
            "district_name": "",
            "assigned_project_ids": "",
            "status": "ACTIVE",
            "created_at": "2024-01-01 00:00:00",
            "last_login": "2024-02-24 16:45:00"
        })

    # Write CSV files
    write_csv("users.csv", users)
    write_csv("projects.csv", projects)
    write_csv("compensation.csv", compensation_records)
    write_csv("legal_disputes.csv", legal_records)
    write_csv("approvals.csv", approval_records)
    write_csv("documentation.csv", documentation_records)
    write_csv("rehabilitation_rr.csv", rr_records)
    write_csv("stakeholders.csv", stakeholder_records)
    write_csv("administrative_performance.csv", admin_records)
    write_csv("project_geospatial.csv", geospatial_records)
    write_csv("project_outcomes.csv", outcome_records)
    write_csv("risk_history.csv", risk_history_records)

    # Generate land_parcels.csv (multiple parcels per project)
    for p in projects:
        p_id = p["project_id"]
        num_parcels = random.randint(3, 8)
        for p_idx in range(1, num_parcels + 1):
            land_parcels.append({
                "parcel_id": f"PCL-{p_id}-{p_idx:02d}",
                "project_id": p_id,
                "parcel_number": f"SY-{random.randint(100, 999)}/{p_idx}",
                "area_acres": round(p["land_area_acres"] / num_parcels, 2),
                "ownership_type": random.choice(["Private", "Government", "Forest", "Community"]),
                "verified_flag": random.choice([1, 1, 1, 0]),
                "dispute_flag": random.choice([0, 0, 1])
            })

    write_csv("land_parcels.csv", land_parcels)

    # Generate lifecycle_timeline.csv
    for p in projects:
        p_id = p["project_id"]
        for stg in LIFECYCLE_STAGES:
            planned = random.randint(30, 90)
            actual = planned + random.randint(-10, 60)
            timeline_records.append({
                "timeline_id": f"TL-{p_id}-{stg[:3].upper()}",
                "project_id": p_id,
                "stage_name": stg,
                "planned_duration_days": planned,
                "actual_duration_days": max(10, actual),
                "stage_status": "COMPLETED" if actual <= planned else ("DELAYED" if actual > planned + 30 else "IN_PROGRESS"),
                "start_date": p["start_date"],
                "end_date": "2024-06-30"
            })

    write_csv("lifecycle_timeline.csv", timeline_records)

    logger.info(f"Successfully generated dataset with {len(projects)} projects and {len(users)} users in '{DATA_DIR}'.")

def write_csv(filename, rows):
    if not rows:
        return
    filepath = DATA_DIR / filename
    headers = list(rows[0].keys())
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    logger.info(f"Wrote {len(rows)} records to {filename}")

if __name__ == "__main__":
    generate_dataset()
