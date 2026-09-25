"""
Consents API Router
===================

File Purpose:
-------------
Exposes HTTP endpoints for recording patient informed consent on the kiosk terminal
before proceeding to medical history taking.

Endpoints:
----------
- `POST /api/consents`: Record consent grant timestamp and legal disclaimer acceptance.

Connected to:
-------------
- `backend/app/schemas/consent.py`: Validates consent request and response.
- `backend/app/repositories/patient_repo.py`: Persists consent records.
- `backend/app/core/dependencies.py`: Injects database session.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.dependencies import get_db
from ..schemas.consent import ConsentGrantRequest, ConsentResponse
from ..repositories.patient_repo import PatientRepository

router = APIRouter(prefix="/api/consents", tags=["Consents"])


@router.post(
    "",
    response_model=ConsentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record patient informed consent"
)
async def record_consent(
    consent_data: ConsentGrantRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Record patient's consent agreement for digital intake, AI-assisted triage,
    and temporary clinical data storage.

    Parameters:
    -----------
    consent_data: ConsentGrantRequest
        Patient ID, acceptance boolean, language, and legal disclaimer text.
    db: AsyncSession
        Injected async database session.

    Returns:
    --------
    ConsentResponse:
        Persisted consent audit trail entry.
    """
    # Step 1: Validate patient existence via PatientRepository.
    # Step 2: Ensure consent_granted is True.
    # Step 3: Call repo.record_consent(consent_data).
    # Step 4: Return populated ConsentResponse.
    repo = PatientRepository(db)
    return await repo.record_consent(consent_data)
