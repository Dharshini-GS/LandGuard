"""
ML Inference, SHAP Explanation, and What-If Simulation Engine for VISTRA.
"""

import sys
import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Tuple
import shap

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from utils.config import (
    MODEL_CLASSIFIER_PATH, MODEL_REGRESSOR_PATH,
    PREPROCESSOR_PATH, MODEL_METADATA_PATH
)
from backend.database import execute_query_one
from utils.logger import get_logger

logger = get_logger("MLService")

class MLService:
    def __init__(self):
        self.model_cls = None
        self.model_reg = None
        self.preprocessor = None
        self.metadata = None
        self.explainer = None
        self.load_models()

    def load_models(self):
        try:
            if MODEL_CLASSIFIER_PATH.exists():
                self.model_cls = joblib.load(MODEL_CLASSIFIER_PATH)
                self.explainer = shap.TreeExplainer(self.model_cls)
            if MODEL_REGRESSOR_PATH.exists():
                self.model_reg = joblib.load(MODEL_REGRESSOR_PATH)
            if PREPROCESSOR_PATH.exists():
                self.preprocessor = joblib.load(PREPROCESSOR_PATH)
            if MODEL_METADATA_PATH.exists():
                with open(MODEL_METADATA_PATH, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
            logger.info("ML Models and SHAP TreeExplainer loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading ML models: {e}")

    def fetch_project_feature_row(self, project_id: str) -> Dict[str, Any]:
        query = """
        SELECT 
            p.project_id, p.project_type, p.current_stage, p.land_area_acres, p.affected_families, p.budget_inr_cr,
            c.disbursement_percentage AS compensation_completion_percentage,
            c.beneficiaries_paid, c.beneficiaries_total,
            l.total_cases, l.pending_cases, l.stay_orders_count,
            d.title_clearance_percentage AS documentation_completion_percentage,
            a.delay_days AS approval_delay_score,
            r.site_readiness_percentage AS rr_completion_score,
            s.stakeholder_response_index AS stakeholder_response_score,
            adm.dept_workload_score, adm.sla_compliance_percentage, adm.bottleneck_score AS administrative_bottleneck_score
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
        row = execute_query_one(query, (project_id,))
        if not row:
            raise ValueError(f"Project '{project_id}' not found in database.")
        return dict(row)

    def prepare_feature_vector(self, row: Dict[str, Any]) -> pd.DataFrame:
        feature_names = self.preprocessor["feature_names"]
        proj_type_map = self.preprocessor["proj_type_map"]
        stage_map = self.preprocessor["stage_map"]

        tot_cases = row.get("total_cases") or 0
        pend_cases = row.get("pending_cases") or 0
        acres = row.get("land_area_acres") or 1.0

        legal_pending_ratio = (pend_cases / tot_cases) if tot_cases > 0 else 0.0
        legal_dispute_density = (tot_cases / (acres / 100.0)) if acres > 0 else 0.0

        proj_type_code = proj_type_map.get(row.get("project_type"), 0)
        stage_code = stage_map.get(row.get("current_stage"), 0)

        data_dict = {
            "land_area_acres": float(row.get("land_area_acres") or 0.0),
            "affected_families": int(row.get("affected_families") or 0),
            "budget_inr_cr": float(row.get("budget_inr_cr") or 0.0),
            "compensation_completion_percentage": float(row.get("compensation_completion_percentage") or 0.0),
            "legal_pending_ratio": float(legal_pending_ratio),
            "legal_dispute_density": float(legal_dispute_density),
            "stay_orders_count": int(row.get("stay_orders_count") or 0),
            "documentation_completion_percentage": float(row.get("documentation_completion_percentage") or 0.0),
            "approval_delay_score": float(row.get("approval_delay_score") or 0.0),
            "rr_completion_score": float(row.get("rr_completion_score") or 0.0),
            "stakeholder_response_score": float(row.get("stakeholder_response_score") or 0.0),
            "administrative_bottleneck_score": float(row.get("administrative_bottleneck_score") or 0.0),
            "dept_workload_score": float(row.get("dept_workload_score") or 0.0),
            "sla_compliance_percentage": float(row.get("sla_compliance_percentage") or 0.0),
            "proj_type_code": proj_type_code,
            "stage_code": stage_code
        }
        return pd.DataFrame([data_dict])[feature_names]

    def predict_risk(self, project_id: str) -> Dict[str, Any]:
        row = self.fetch_project_feature_row(project_id)
        X = self.prepare_feature_vector(row)

        prob = float(self.model_cls.predict_proba(X)[0, 1])
        risk_score = round(prob * 100.0, 1)

        expected_delay = int(max(0, self.model_reg.predict(X)[0]))

        if risk_score > 80.0:
            category = "CRITICAL"
        elif risk_score > 60.0:
            category = "HIGH"
        elif risk_score > 30.0:
            category = "MEDIUM"
        else:
            category = "LOW"

        # Determine highest risk stage based on sub-metrics
        highest_stage = self._calculate_highest_risk_stage(row)

        return {
            "project_id": project_id,
            "delay_probability": round(prob, 4),
            "risk_score": risk_score,
            "risk_category": category,
            "expected_delay_days": expected_delay,
            "highest_risk_stage": highest_stage,
            "model_version": self.metadata.get("model_version", "v1.0.0") if self.metadata else "v1.0.0"
        }

    def explain_shap(self, project_id: str) -> Dict[str, Any]:
        row = self.fetch_project_feature_row(project_id)
        X = self.prepare_feature_vector(row)

        prob = float(self.model_cls.predict_proba(X)[0, 1])
        category = "CRITICAL" if prob > 0.8 else ("HIGH" if prob > 0.6 else ("MEDIUM" if prob > 0.3 else "LOW"))

        shap_values = self.explainer.shap_values(X)[0]
        base_val = float(self.explainer.expected_value)

        feature_names = self.preprocessor["feature_names"]
        human_map = self.preprocessor["human_map"]

        factors = []
        for name, val, feat_val in zip(feature_names, shap_values, X.iloc[0]):
            label = human_map.get(name, name)
            impact_dir = "INCREASES_RISK" if val > 0 else "REDUCES_RISK"

            if name == "legal_pending_ratio" and val > 0:
                explanation = f"High ratio of unresolved legal disputes ({feat_val:.0%}) increases project delay probability."
            elif name == "compensation_completion_percentage" and val > 0:
                explanation = f"Low compensation disbursement progress ({feat_val:.1f}%) contributes significantly to risk."
            elif name == "approval_delay_score" and val > 0:
                explanation = f"Clearance approval delays ({feat_val:.0f} days) escalate lifecycle risk."
            elif val > 0:
                explanation = f"High {label} contributes positively to delay risk."
            else:
                explanation = f"Favorable {label} helps lower overall project risk."

            factors.append({
                "feature_name": name,
                "human_label": label,
                "shap_value": round(float(val), 4),
                "feature_value": float(feat_val),
                "impact_direction": impact_dir,
                "explanation": explanation
            })

        # Sort factors by magnitude of impact
        factors.sort(key=lambda x: abs(x["shap_value"]), reverse=True)

        top_drivers = [f["human_label"] for f in factors if f["impact_direction"] == "INCREASES_RISK"][:3]
        drivers_str = ", ".join(top_drivers) if top_drivers else "no major bottleneck"
        human_summary = f"Project '{project_id}' predicted at {prob*100:.1f}% delay probability ({category}). Primary delay drivers: {drivers_str}."

        return {
            "project_id": project_id,
            "delay_probability": round(prob, 4),
            "risk_category": category,
            "base_value": round(base_val, 4),
            "top_contributors": factors[:8],  # Top 8 factors
            "summary_human": human_summary
        }

    def simulate_what_if(self, project_id: str, mods: Dict[str, Any]) -> Dict[str, Any]:
        row = self.fetch_project_feature_row(project_id)

        # Initial risk calculation
        init_res = self.predict_risk(project_id)
        init_score = init_res["risk_score"]
        init_cat = init_res["risk_category"]

        # Apply user modifications to copy of row
        mod_row = row.copy()
        if mods.get("compensation_completion_pct") is not None:
            mod_row["compensation_completion_percentage"] = mods["compensation_completion_pct"]

        if mods.get("pending_legal_cases") is not None:
            mod_row["pending_cases"] = mods["pending_legal_cases"]

        if mods.get("approval_delay_days") is not None:
            mod_row["approval_delay_score"] = mods["approval_delay_days"]

        if mods.get("documentation_completion_pct") is not None:
            mod_row["documentation_completion_percentage"] = mods["documentation_completion_pct"]

        if mods.get("rr_completion_pct") is not None:
            mod_row["rr_completion_score"] = mods["rr_completion_pct"]

        if mods.get("stakeholder_response_idx") is not None:
            mod_row["stakeholder_response_score"] = mods["stakeholder_response_idx"]

        # Run model on modified feature vector
        X_mod = self.prepare_feature_vector(mod_row)
        sim_prob = float(self.model_cls.predict_proba(X_mod)[0, 1])
        sim_score = round(sim_prob * 100.0, 1)

        sim_delay = int(max(0, self.model_reg.predict(X_mod)[0]))

        if sim_score > 80.0:
            sim_cat = "CRITICAL"
        elif sim_score > 60.0:
            sim_cat = "HIGH"
        elif sim_score > 30.0:
            sim_cat = "MEDIUM"
        else:
            sim_cat = "LOW"

        risk_reduction = round(init_score - sim_score, 1)

        return {
            "project_id": project_id,
            "initial_risk_score": init_score,
            "initial_risk_category": init_cat,
            "simulated_risk_score": sim_score,
            "simulated_risk_category": sim_cat,
            "risk_reduction": risk_reduction,
            "simulated_expected_delay_days": sim_delay,
            "disclaimer": "Model-based scenario estimate, not a guaranteed outcome."
        }

    def _calculate_highest_risk_stage(self, row: Dict[str, Any]) -> str:
        comp_pct = row.get("compensation_completion_percentage") or 100.0
        pending_legal = row.get("pending_cases") or 0
        approval_delay = row.get("approval_delay_score") or 0
        doc_pct = row.get("documentation_completion_percentage") or 100.0
        rr_pct = row.get("rr_completion_score") or 100.0

        scores = {
            "Legal Resolution": pending_legal * 5.0,
            "Compensation": (100.0 - comp_pct) * 0.8,
            "Approval": approval_delay * 0.7,
            "Documentation": (100.0 - doc_pct) * 0.6,
            "R&R": (100.0 - rr_pct) * 0.6
        }
        return max(scores, key=scores.get)

ml_service_instance = MLService()
