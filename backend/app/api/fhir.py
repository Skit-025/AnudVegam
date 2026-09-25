"""
FHIR Export API Router
======================

File Purpose:
-------------
Exposes HTTP endpoints for exporting patient intake data, scanned records, and doctor notes
as ABDM-compliant Fast Healthcare Interoperability Resources (FHIR R4) JSON bundles.

Endpoints:
----------
- `POST /api/sessions/{id}/fhir-export`: Compile and return standardized ABDM FHIR JSON bundle.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.dependencies import get_db
from ..schemas.fhir import FHIRExportResponse
from ..services.fhir_exporter import FHIRExporterService

router = APIRouter(prefix="/api/sessions", tags=["FHIR Export"])


@router.post(
    "/{session_id}/fhir-export",
    response_model=FHIRExportResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate mocked FHIR JSON export"
)
async def export_session_to_fhir(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Compile the completed patient encounter into an ABDM FHIR R4 Bundle in real time.
    """
    exporter = FHIRExporterService(db)
    bundle_json = await exporter.generate_fhir_bundle(session_id)
    return FHIRExportResponse(
        id=f"fhir-export-{session_id[:8]}",
        session_id=session_id,
        fhir_resource_type="Bundle",
        status="MOCKED_ABDM_READY",
        fhir_json_payload=bundle_json,
        abdm_care_context_id=f"CARE_CONTEXT_{session_id[:8]}",
        created_at=datetime.now(timezone.utc)
    )
