"""
FastAPI Server Entry Point for VISTRA.
Predictive Analytics System for Early Detection of Land Acquisition Delays (SIH26017).
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.routes.auth_routes import router as auth_router
from backend.routes.project_routes import router as project_router
from backend.routes.risk_routes import router as risk_router
from backend.routes.predict_routes import router as predict_router
from backend.routes.alert_routes import router as alert_router
from backend.routes.map_routes import router as map_router
from backend.routes.report_routes import router as report_router
from backend.routes.admin_routes import router as admin_router
from backend.routes.ai_routes import router as ai_router

from utils.config import SYNTHETIC_DATA_BANNER, SYNTHETIC_DATA_DISCLAIMER
from utils.logger import get_logger

logger = get_logger("FastAPIApp")

app = FastAPI(
    title="VISTRA — Backend API",
    description="Early-Warning & Decision-Support Platform for Land Acquisition Projects (SIH26017)",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router)
app.include_router(project_router)
app.include_router(risk_router)
app.include_router(predict_router)
app.include_router(alert_router)
app.include_router(map_router)
app.include_router(report_router)
app.include_router(admin_router)
app.include_router(ai_router)

@app.get("/")
def root():
    return {
        "app": "VISTRA",
        "tagline": "Predict Before It Delays.",
        "notice": SYNTHETIC_DATA_BANNER,
        "disclaimer": SYNTHETIC_DATA_DISCLAIMER,
        "status": "ONLINE"
    }

# Global Exception Handler (friendly user-facing message, detailed internal logs)
@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Unable to process request. Please try again later."}
    )
