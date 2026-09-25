"""
Consent Pydantic Schemas
========================

File Purpose:
-------------
Defines request and response schemas for capturing patient informed consent
for kiosk intake and AI clinical documentation.

Connected to:
-------------
- `backend/app/api/consents.py`: Request body and response typing.
- `backend/app/repositories/consent_repo.py`: Schema data mapping to ORM model.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ConsentGrantRequest(BaseModel):
    """Payload for submitting consent agreement on the kiosk."""
    patient_id: str = Field(..., description="UUID of the patient granting consent")
    consent_granted: bool = Field(default=True, description="True if accepted")
    consent_text: str = Field(..., description="Exact legal text displayed on screen")
    language: str = Field(default="en", description="Language of displayed text")


class ConsentResponse(BaseModel):
    """Response returned after recording consent."""
    id: str
    patient_id: str
    consent_granted: bool
    language: str
    granted_at: datetime

    class Config:
        from_attributes = True
