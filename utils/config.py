import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_DIR = BASE_DIR / "database"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"
SCRIPTS_DIR = BASE_DIR / "scripts"

DATABASE_PATH = DATABASE_DIR / "landguard.db"
MODEL_CLASSIFIER_PATH = MODELS_DIR / "delay_model.pkl"
MODEL_REGRESSOR_PATH = MODELS_DIR / "delay_regressor.pkl"
PREPROCESSOR_PATH = MODELS_DIR / "preprocessor.pkl"
MODEL_METADATA_PATH = MODELS_DIR / "model_metadata.json"

# Create directories if they don't exist
for d in [DATA_DIR, DATABASE_DIR, MODELS_DIR, REPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Security & JWT
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "landguard-ai-secure-secret-key-2026-sih26017")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 60 * 24  # 24 hours

# Risk thresholds
RISK_THRESHOLDS = {
    "LOW": (0.0, 30.0),
    "MEDIUM": (30.1, 60.0),
    "HIGH": (60.1, 80.0),
    "CRITICAL": (80.1, 100.0)
}

# Synthetic Prototype Disclaimers
SYNTHETIC_DATA_BANNER = "DATA TYPE: SYNTHETIC PROTOTYPE"
SYNTHETIC_DATA_DISCLAIMER = (
    "Prototype trained and demonstrated using synthetic/historical-like data. "
    "The system is designed to be retrained and validated using authorized government data when available."
)
