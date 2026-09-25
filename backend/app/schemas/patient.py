"""
Patient Pydantic Schemas
========================

File Purpose:
-------------
Defines request and response validation schemas for patient registration, identification,
and mock ABHA lookup.

Connected to:
-------------
- `backend/app/api/patients.py`: Request body and response_model typing.
- `backend/app/repositories/patient_repo.py`: Schema data mapping to ORM model.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class PatientCreate(BaseModel):
    """Payload for registering or identifying a patient at the kiosk."""
    abha_id: Optional[str] = Field(default=None, description="14-digit ABHA number if available")
    name: str = Field(..., min_length=2, max_length=128, description="Patient full name")
    age: int = Field(..., ge=0, le=125, description="Patient age")
    gender: str = Field(..., description="MALE, FEMALE, or OTHER")
    phone: Optional[str] = Field(default=None, max_length=20, description="Mobile contact number")
    preferred_language: str = Field(default="en", max_length=8, description="ISO language code (e.g. en, hi)")


class PatientResponse(PatientCreate):
    """Response returned upon patient registration or lookup."""
    id: str = Field(..., description="Internal UUID of the patient")
    created_at: datetime

    class Config:
        from_attributes = True


class MockABHALookupRequest(BaseModel):
    """Request for simulating ABHA / Aadhaar verification."""
    abha_id: str = Field(..., description="14-digit ABHA number")


class MockABHALookupResponse(BaseModel):
    """Simulated ABHA profile returned from mock ABDM gateway."""
    verified: bool
    abha_id: str
    name: str
    gender: str
    age: int
    phone: Optional[str] = None
