"""
Case Summary Pydantic Schemas
=============================

File Purpose:
-------------
Defines request and response schemas for AI draft case summaries, physician edits,
review sign-offs, and mandatory safety disclaimers.

Connected to:
-------------
- `backend/app/api/summaries.py`: Endpoints for summary generation and physician edit.
- `backend/app/models/summary.py`: Maps to `CaseSummaryModel`.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class CaseSummaryResponse(BaseModel):
    """Structured clinical summary returned to doctor and kiosk."""
    id: str
    session_id: str
    chief_complaint: str
    hpi: str
    past_history: Optional[str] = None
    current_medications: Optional[str] = None
    ai_draft_text: str
    physician_edited_text: Optional[str] = None
    clinical_assessment: Optional[str] = None
    reviewed: bool
    reviewed_by_doctor_id: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    disclaimer: str = Field(
        default="AI-drafted. Physician review required before use.",
        description="Mandatory API disclaimer"
    )

    class Config:
        from_attributes = True


class PhysicianSummaryEditRequest(BaseModel):
    """Payload when attending doctor edits and signs off on the case summary."""
    doctor_id: str = Field(..., description="Unique ID of the reviewing physician")
    physician_edited_text: str = Field(..., description="Doctor verified clinical notes")
    clinical_assessment: Optional[str] = Field(default=None, description="Provisional diagnosis or clinical assessment")
    reviewed: bool = Field(default=True, description="Doctor sign-off flag")
