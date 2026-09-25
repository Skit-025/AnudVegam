"""
MediKiosk Main Backend - FastAPI Application Entrypoint
======================================================

File Purpose:
-------------
Initializes the FastAPI application, mounts API routers, configures global CORS middleware,
manages lifespan database connection hooks, and serves as the central orchestration server
for MediKiosk (SIH26047).

What it does:
-------------
1. Creates FastAPI application with OpenAPI documentation metadata.
2. Configures CORS allowing communication from the React frontend (port 3000).
3. Mounts modular API routers:
   - `/api/patients`: Patient registration & mock ABHA lookup
   - `/api/consents`: Informed consent recording
   - `/api/sessions`: Encounter lifecycle, Q&A responses, next-question routing
   - `/api/documents`: Prescription/lab report uploads and OCR integration
   - `/api/summaries`: Clinical draft generation and doctor review/confirmation
   - `/api/fhir`: ABDM-compliant FHIR R4 JSON export
4. Handles health check and readiness probes.
5. Automatically provisions all 9 database tables via `init_db()` on startup.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.dependencies import init_db
from .api.patients import router as patients_router
from .api.consents import router as consents_router
from .api.sessions import router as sessions_router
from .api.documents import router as documents_router
from .api.summaries import router as summaries_router
from .api.fhir import router as fhir_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager for startup and shutdown hooks.
    """
    # Initialize all database tables on application start
    await init_db()
    yield


app = FastAPI(
    title="MediKiosk Main Backend Orchestrator",
    version="1.0.0",
    description="Main orchestration server and REST API for MediKiosk Patient Case-Taking Software (SIH26047)",
    lifespan=lifespan
)

# Configure Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(patients_router)
app.include_router(consents_router)
app.include_router(sessions_router)
app.include_router(documents_router)
app.include_router(summaries_router)
app.include_router(fhir_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify backend operational status.

    Returns:
    --------
    dict: Service health indicator.
    """
    return {
        "status": "healthy",
        "service": "medikiosk-main-backend",
        "version": "1.0.0"
    }
