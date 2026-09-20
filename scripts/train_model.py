"""
ML Training Pipeline for VISTRA.
Trains XGBoost Classifier (delay probability) and Regressor (expected delay days).
Includes feature engineering, baseline comparisons (Logistic Regression, Random Forest),
SHAP Explainer initialization, and metadata export to models/ directory.
"""

import sys
import json
import sqlite3
import joblib
from pathlib import Path
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, mean_absolute_error, r2_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
import shap

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from utils.config import (
    DATABASE_PATH, MODEL_CLASSIFIER_PATH, MODEL_REGRESSOR_PATH,
    PREPROCESSOR_PATH, MODEL_METADATA_PATH
)
from utils.logger import get_logger

logger = get_logger("MLTrainer")

FEATURE_NAMES = [
    "land_area_acres",
    "affected_families",
    "budget_inr_cr",
    "compensation_completion_percentage",
    "legal_pending_ratio",
    "legal_dispute_density",
    "stay_orders_count",
    "documentation_completion_percentage",
    "approval_delay_score",
    "rr_completion_score",
    "stakeholder_response_score",
    "administrative_bottleneck_score",
    "dept_workload_score",
    "sla_compliance_percentage",
    "proj_type_code",
    "stage_code"
]

FEATURE_HUMAN_MAP = {
    "land_area_acres": "Land Area (Acres)",
    "affected_families": "Affected Families Count",
    "budget_inr_cr": "Project Budget (INR Cr)",
    "compensation_completion_percentage": "Compensation Payment Progress (%)",
    "legal_pending_ratio": "Pending Legal Case Ratio",
    "legal_dispute_density": "Dispute Density per 100 Acres",
    "stay_orders_count": "Active Judicial Stay Orders",
    "documentation_completion_percentage": "Title Clearance & Doc Verification (%)",
    "approval_delay_score": "Clearance Approval Delay (Days)",
    "rr_completion_score": "R&R Resettlement Progress (%)",
    "stakeholder_response_score": "Community Opposition Index",
    "administrative_bottleneck_score": "Administrative Processing Bottleneck",
    "dept_workload_score": "Department Workload Score",
    "sla_compliance_percentage": "SLA Compliance Rate (%)",
    "proj_type_code": "Project Infrastructure Sector",
    "stage_code": "Lifecycle Acquisition Stage"
}

def load_data_from_db():
    conn = sqlite3.connect(DATABASE_PATH)
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
        adm.dept_workload_score, adm.sla_compliance_percentage, adm.bottleneck_score AS administrative_bottleneck_score,
        o.delay_flag, o.delay_days
    FROM projects p
    LEFT JOIN compensation c ON p.project_id = c.project_id
    LEFT JOIN legal_disputes l ON p.project_id = l.project_id
    LEFT JOIN documentation d ON p.project_id = d.project_id
    LEFT JOIN approvals a ON p.project_id = a.project_id
    LEFT JOIN rehabilitation_rr r ON p.project_id = r.project_id
    LEFT JOIN stakeholders s ON p.project_id = s.project_id
    LEFT JOIN administrative_performance adm ON p.project_id = adm.project_id
    LEFT JOIN project_outcomes o ON p.project_id = o.project_id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def feature_engineering(df):
    df = df.copy()
    # Compute derived ratio features
    df["legal_pending_ratio"] = df.apply(
        lambda r: (r["pending_cases"] / r["total_cases"]) if r["total_cases"] > 0 else 0.0, axis=1
    )
    df["legal_dispute_density"] = df.apply(
        lambda r: (r["total_cases"] / (r["land_area_acres"] / 100.0)) if r["land_area_acres"] > 0 else 0.0, axis=1
    )

    # Encode categorical features deterministically
    proj_type_map = {t: idx for idx, t in enumerate(df["project_type"].unique())}
    stage_map = {s: idx for idx, s in enumerate(df["current_stage"].unique())}

    df["proj_type_code"] = df["project_type"].map(proj_type_map)
    df["stage_code"] = df["current_stage"].map(stage_map)

    preprocessor = {
        "proj_type_map": proj_type_map,
        "stage_map": stage_map,
        "feature_names": FEATURE_NAMES,
        "human_map": FEATURE_HUMAN_MAP
    }

    return df, preprocessor

def train_and_evaluate():
    logger.info("Loading dataset from SQLite...")
    raw_df = load_data_from_db()
    df, preprocessor = feature_engineering(raw_df)

    X = df[FEATURE_NAMES]
    y_cls = df["delay_flag"]
    y_reg = df["delay_days"]

    X_train, X_test, y_train_c, y_test_c, y_train_r, y_test_r = train_test_split(
        X, y_cls, y_reg, test_size=0.2, random_state=42, stratify=y_cls
    )

    # 1. Baseline Models Evaluation
    lr = LogisticRegression(max_iter=1000, random_state=42)
    lr.fit(X_train, y_train_c)
    lr_acc = accuracy_score(y_test_c, lr.predict(X_test))

    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train_c)
    rf_acc = accuracy_score(y_test_c, rf.predict(X_test))

    logger.info(f"Baseline Accuracies - Logistic Regression: {lr_acc:.4f}, Random Forest: {rf_acc:.4f}")

    # 2. Primary Model: XGBoost Classifier
    model_cls = xgb.XGBClassifier(
        n_estimators=150,
        max_depth=5,
        learning_rate=0.05,
        random_state=42,
        eval_metric="logloss"
    )
    model_cls.fit(X_train, y_train_c)

    preds_c = model_cls.predict(X_test)
    probs_c = model_cls.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test_c, preds_c)
    prec = precision_score(y_test_c, preds_c, zero_division=0)
    rec = recall_score(y_test_c, preds_c, zero_division=0)
    f1 = f1_score(y_test_c, preds_c, zero_division=0)
    roc = roc_auc_score(y_test_c, probs_c)

    logger.info(f"XGBoost Classifier - Accuracy: {acc:.4f}, Precision: {prec:.4f}, Recall: {rec:.4f}, F1: {f1:.4f}, ROC-AUC: {roc:.4f}")

    # 3. Primary Model: XGBoost Regressor
    model_reg = xgb.XGBRegressor(
        n_estimators=150,
        max_depth=5,
        learning_rate=0.05,
        random_state=42
    )
    model_reg.fit(X_train, y_train_r)

    preds_r = model_reg.predict(X_test)
    mae = mean_absolute_error(y_test_r, preds_r)
    r2 = r2_score(y_test_r, preds_r)

    logger.info(f"XGBoost Regressor - MAE: {mae:.2f} days, R2 Score: {r2:.4f}")

    # 4. Feature Importance
    importances = model_cls.feature_importances_
    feat_imp = {feat: float(imp) for feat, imp in zip(FEATURE_NAMES, importances)}

    # Save Models & Artifacts
    joblib.dump(model_cls, MODEL_CLASSIFIER_PATH)
    joblib.dump(model_reg, MODEL_REGRESSOR_PATH)
    joblib.dump(preprocessor, PREPROCESSOR_PATH)

    metadata = {
        "model_version": "v1.0.0",
        "trained_date": "2026-08-26",
        "dataset_size": len(df),
        "feature_count": len(FEATURE_NAMES),
        "metrics": {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc, 4),
            "mae_days": round(mae, 2),
            "r2_score": round(r2, 4),
            "baseline_lr_acc": round(lr_acc, 4),
            "baseline_rf_acc": round(rf_acc, 4)
        },
        "feature_importance": feat_imp,
        "human_feature_mapping": FEATURE_HUMAN_MAP
    }

    with open(MODEL_METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"Models successfully trained and saved to '{MODEL_CLASSIFIER_PATH.parent}'.")

if __name__ == "__main__":
    train_and_evaluate()
