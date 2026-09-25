"""
FHIR Export Pydantic Schemas
============================

File Purpose:
-------------
Defines request and response schemas for ABDM-compliant FHIR R4 JSON bundle export.

Connected to:
-------------
- `backend/app/api/fhir.py`: Endpoint `/api/sessions/{id}/fhir-export`.
- `backend/app/models/fhir.py`: Maps to `FHIRExportModel`.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class FHIRExportResponse(BaseModel):
    """Payload representing the generated FHIR JSON bundle."""
    id: str
    session_id: str
    fhir_resource_type: str = "Bundle"
    status: str = "MOCKED"
    fhir_json_payload: Dict[str, Any] = Field(..., description="Complete FHIR JSON bundle")
    abdm_care_context_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
