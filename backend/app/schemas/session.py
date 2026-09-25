"""
Session Pydantic Schemas
========================

File Purpose:
-------------
Defines request and response schemas for kiosk intake session creation,
session lifecycle tracking, and full session clinical details for doctor review.

Connected to:
-------------
- `backend/app/api/sessions.py`: Handlers for `/api/sessions` and `/api/sessions/{id}`.
- `backend/app/models/session.py`: Maps to `SessionModel`.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from .patient import PatientResponse
from .response import HistoryResponseItem
from .document import DocumentResponseItem
from .summary import CaseSummaryResponse


class SessionCreateRequest(BaseModel):
    """Payload to initiate a new case-taking session."""
    patient_id: str = Field(..., description="UUID of the patient")
    mode: str = Field(default="ALLOPATHIC", description="Clinical mode: ALLOPATHIC or AYUSH")


class SessionResponse(BaseModel):
    """Basic session response model."""
    id: str
    patient_id: str
    mode: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class CompleteSessionDetail(BaseModel):
    """
    Comprehensive session view returned to the doctor for pre-consultation review.
    """
    id: str
    mode: str
    status: str
    patient: PatientResponse
    responses: List[HistoryResponseItem] = Field(default_factory=list)
    documents: List[DocumentResponseItem] = Field(default_factory=list)
    summary: Optional[CaseSummaryResponse] = None
    created_at: datetime

    class Config:
        from_attributes = True
