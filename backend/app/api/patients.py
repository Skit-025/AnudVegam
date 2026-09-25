"""
Patients API Router
===================

File Purpose:
-------------
Exposes HTTP endpoints for patient identification, kiosk registration,
and mock ABHA / Aadhaar verification.

Endpoints:
----------
- `POST /api/patients`: Register new patient or retrieve existing profile by ABHA/Phone.
- `POST /api/patients/lookup-abha`: Query mock ABDM gateway to verify ABHA ID.

Connected to:
-------------
- `backend/app/schemas/patient.py`: Validates request and response bodies.
- `backend/app/repositories/patient_repo.py`: Persists patient demographic data.
- `backend/app/core/dependencies.py`: Injects database session.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.dependencies import get_db
from ..schemas.patient import PatientCreate, PatientResponse, MockABHALookupRequest, MockABHALookupResponse
from ..repositories.patient_repo import PatientRepository
from ..core.security import SecurityManager

router = APIRouter(prefix="/api/patients", tags=["Patients"])
security = SecurityManager()


@router.post(
    "",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register or identify patient"
)
async def create_or_identify_patient(
    patient_data: PatientCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new patient or retrieve existing patient record via ABHA ID.

    Parameters:
    -----------
    patient_data: PatientCreate
        Demographic and identifier information.
    db: AsyncSession
        Injected async database session.

    Returns:
    --------
    PatientResponse:
        Created or retrieved patient profile with internal UUID.
    """
    # Step 1: Initialize PatientRepository(db).
    # Step 2: If abha_id provided, check if patient already exists.
    # Step 3: If patient exists, return existing profile.
    # Step 4: If new patient, create in database via repo.create(patient_data).
    # Step 5: Return PatientResponse.
    repo = PatientRepository(db)
    return await repo.create(patient_data)


@router.post(
    "/lookup-abha",
    response_model=MockABHALookupResponse,
    summary="Mock ABHA / Aadhaar KYC lookup"
)
async def lookup_mock_abha(request: MockABHALookupRequest):
    """
    Simulate ABHA digital healthcare ID lookup and KYC verification.

    Parameters:
    -----------
    request: MockABHALookupRequest
        14-digit ABHA number.

    Returns:
    --------
    MockABHALookupResponse:
        Simulated verified demographic profile.
    """
    # Step 1: Call security.verify_mock_abha(request.abha_id).
    # Step 2: Return simulated demographic profile.
    verification = security.verify_mock_abha(request.abha_id)
    return MockABHALookupResponse(
        verified=verification["verified"],
        abha_id=request.abha_id,
        name="Ramesh Kumar",
        gender="MALE",
        age=45,
        phone="9876543210"
    )
