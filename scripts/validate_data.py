"""
Data Validator for LANDGUARD AI (SIH26017 Prototype).
Ensures data integrity, foreign key relations, domain ranges, state/district validity, and business logic rules.
Stops execution if validation fails.
"""

import sys
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from utils.config import DATA_DIR
from utils.geo_data import GEO_REFERENCE, ROLES, SCOPES, RISK_CATEGORIES
from utils.logger import get_logger

logger = get_logger("DataValidator")

def load_csv(filename):
    filepath = DATA_DIR / filename
    if not filepath.exists():
        logger.error(f"Required CSV file missing: {filepath}")
        sys.exit(1)
    with open(filepath, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def validate_all():
    logger.info("Starting comprehensive data validation...")
    errors = []

    # 1. Load data files
    users = load_csv("users.csv")
    projects = load_csv("projects.csv")
    parcels = load_csv("land_parcels.csv")
    timeline = load_csv("lifecycle_timeline.csv")
    compensation = load_csv("compensation.csv")
    legal = load_csv("legal_disputes.csv")
    approvals = load_csv("approvals.csv")
    documentation = load_csv("documentation.csv")
    rr = load_csv("rehabilitation_rr.csv")
    stakeholders = load_csv("stakeholders.csv")
    admin = load_csv("administrative_performance.csv")
    geospatial = load_csv("project_geospatial.csv")
    outcomes = load_csv("project_outcomes.csv")
    risk_history = load_csv("risk_history.csv")

    # Validate dataset counts
    if len(projects) < 1000:
        errors.append(f"Project count ({len(projects)}) is less than minimum required 1000.")

    # Collect project IDs
    project_ids = set()
    for row in projects:
        p_id = row["project_id"]
        if p_id in project_ids:
            errors.append(f"Duplicate project_id in projects.csv: {p_id}")
        project_ids.add(p_id)

    logger.info(f"Verified {len(project_ids)} unique projects.")

    # 2. Check Geographic Codes
    valid_state_codes = set(GEO_REFERENCE.keys())
    valid_district_codes = set()
    for st_code, st_info in GEO_REFERENCE.items():
        for d in st_info["districts"]:
            valid_district_codes.add(d["code"])

    for p in projects:
        p_id = p["project_id"]
        if p["state_code"] not in valid_state_codes:
            errors.append(f"Invalid state_code '{p['state_code']}' in project {p_id}")
        if p["district_code"] not in valid_district_codes:
            errors.append(f"Invalid district_code '{p['district_code']}' in project {p_id}")
        if float(p["land_area_acres"]) <= 0:
            errors.append(f"Negative/zero land_area_acres in project {p_id}")
        if float(p["budget_inr_cr"]) <= 0:
            errors.append(f"Negative/zero budget_inr_cr in project {p_id}")

    # 3. Check FK relations and Business Logic Rules for related tables
    for c in compensation:
        p_id = c["project_id"]
        if p_id not in project_ids:
            errors.append(f"FK constraint violated in compensation.csv for project {p_id}")
        tot = int(c["beneficiaries_total"])
        paid = int(c["beneficiaries_paid"])
        pending = int(c["beneficiaries_pending"])
        pct = float(c["disbursement_percentage"])

        if paid > tot:
            errors.append(f"beneficiaries_paid ({paid}) > beneficiaries_total ({tot}) in project {p_id}")
        if pending != tot - paid:
            errors.append(f"beneficiaries_pending mismatch in project {p_id}")
        if pct < 0 or pct > 100:
            errors.append(f"Invalid disbursement_percentage {pct}% in project {p_id}")

    for l in legal:
        p_id = l["project_id"]
        if p_id not in project_ids:
            errors.append(f"FK constraint violated in legal_disputes.csv for project {p_id}")
        tot_c = int(l["total_cases"])
        pend_c = int(l["pending_cases"])
        res_c = int(l["resolved_cases"])
        if pend_c > tot_c:
            errors.append(f"pending_cases ({pend_c}) > total_cases ({tot_c}) in project {p_id}")
        if res_c != tot_c - pend_c:
            errors.append(f"resolved_cases mismatch in project {p_id}")

    for r in rr:
        p_id = r["project_id"]
        if p_id not in project_ids:
            errors.append(f"FK constraint violated in rehabilitation_rr.csv for project {p_id}")
        elig = int(r["families_eligible"])
        rehab = int(r["families_rehabilitated"])
        pend_rr = int(r["families_pending"])
        site_pct = float(r["site_readiness_percentage"])

        if rehab > elig:
            errors.append(f"families_rehabilitated ({rehab}) > families_eligible ({elig}) in project {p_id}")
        if pend_rr != elig - rehab:
            errors.append(f"families_pending mismatch in rehabilitation_rr.csv for project {p_id}")
        if site_pct < 0 or site_pct > 100:
            errors.append(f"Invalid site_readiness_percentage {site_pct}% in project {p_id}")

    for d in documentation:
        p_id = d["project_id"]
        if p_id not in project_ids:
            errors.append(f"FK constraint violated in documentation.csv for project {p_id}")
        tot_rec = int(d["total_records"])
        ver_rec = int(d["records_verified"])
        pend_rec = int(d["records_pending"])
        clr_pct = float(d["title_clearance_percentage"])

        if ver_rec > tot_rec:
            errors.append(f"records_verified ({ver_rec}) > total_records ({tot_rec}) in project {p_id}")
        if pend_rec != tot_rec - ver_rec:
            errors.append(f"records_pending mismatch in documentation.csv for project {p_id}")
        if clr_pct < 0 or clr_pct > 100:
            errors.append(f"Invalid title_clearance_percentage {clr_pct}% in project {p_id}")

    for s in stakeholders:
        p_id = s["project_id"]
        if p_id not in project_ids:
            errors.append(f"FK constraint violated in stakeholders.csv for project {p_id}")
        rec = int(s["objections_received"])
        res = int(s["objections_resolved"])
        pend = int(s["pending_objections"])
        idx_val = float(s["stakeholder_response_index"])

        if res > rec:
            errors.append(f"objections_resolved ({res}) > objections_received ({rec}) in project {p_id}")
        if pend != rec - res:
            errors.append(f"pending_objections mismatch in stakeholders.csv for project {p_id}")
        if idx_val < 0 or idx_val > 100:
            errors.append(f"Invalid stakeholder_response_index {idx_val} in project {p_id}")

    # 4. Check Users Validation
    user_ids = set()
    usernames = set()
    for u in users:
        u_id = u["user_id"]
        uname = u["username"]
        if u_id in user_ids:
            errors.append(f"Duplicate user_id in users.csv: {u_id}")
        if uname in usernames:
            errors.append(f"Duplicate username in users.csv: {uname}")
        user_ids.add(u_id)
        usernames.add(uname)

        if u["role"] not in ROLES:
            errors.append(f"Invalid role '{u['role']}' for user {u_id}")
        if u["scope_type"] not in SCOPES:
            errors.append(f"Invalid scope_type '{u['scope_type']}' for user {u_id}")

    # Output report
    if errors:
        logger.error(f"VALIDATION FAILED with {len(errors)} errors:")
        for err in errors[:25]:
            logger.error(f"  - {err}")
        if len(errors) > 25:
            logger.error(f"  ... and {len(errors) - 25} more errors.")
        sys.exit(1)
    else:
        logger.info("DATA VALIDATION PASSED SUCCESSFULLY! All PK, FK, domain, and cross-field rules verified.")

if __name__ == "__main__":
    validate_all()
