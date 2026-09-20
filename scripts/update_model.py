"""
Model Update Script for VISTRA.
Triggers retraining of ML models from the current database state.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.train_model import train_and_evaluate
from utils.logger import get_logger

logger = get_logger("ModelUpdater")

def update_model():
    logger.info("Triggering model retrain process...")
    train_and_evaluate()
    logger.info("Model retrain completed successfully.")

if __name__ == "__main__":
    update_model()
