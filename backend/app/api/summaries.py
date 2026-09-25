"""
Summaries API Router
====================

File Purpose:
-------------
Exposes HTTP endpoints for triggering AI clinical case-note draft generation,
capturing physician edits, and recording final doctor sign-off.

Endpoints:
----------
- `POST /api/sessions/{id}/summary`: Ingests interview Q&A and OCR entities, invokes Summarizer AI.
- `PUT /api/sessions/{id}/summary`: Saves physician modifications and locks summary (`reviewed = True`).

API Safety Rule:
----------------
Every summary response MUST visibly and programmatically carry the disclaimer:
"AI-drafted. Physician review required before use." and mark `reviewed = False`
until explicit doctor confirmation.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.dependencies import get_db, get_dialogue_client, get_ocr_client, get_summarizer_client
from ..schemas.summary import CaseSummaryResponse, PhysicianSummaryEditRequest
from ..services.case_orchestrator import CaseOrchestratorService
from ..repositories.summary_repo import SummaryRepository
from ..clients.dialogue_client import DialogueClient
from ..clients.ocr_client import OCRClient
from ..clients.summarizer_client import SummarizerClient

router = APIRouter(prefix="/api/sessions", tags=["Summaries"])


@router.post(
    "/{session_id}/summary",
    response_model=CaseSummaryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate AI case-summary draft"
)
async def generate_summary(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    dialogue_client: DialogueClient = Depends(get_dialogue_client),
    ocr_client: OCRClient = Depends(get_ocr_client),
    summarizer_client: SummarizerClient = Depends(get_summarizer_client)
):
    """
    Trigger the LLM summarizer pipeline to compile an intake case summary draft in real time.
    """
    orchestrator = CaseOrchestratorService(db, dialogue_client, ocr_client, summarizer_client)
    summary_data = await orchestrator.trigger_case_summary(session_id)
    return summary_data


@router.put(
    "/{session_id}/summary",
    response_model=CaseSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Save physician edits and confirmation"
)
async def update_physician_summary(
    session_id: str,
    edit_data: PhysicianSummaryEditRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Save attending physician modifications, assessment, and sign-off.
    Enforces the human-in-the-loop requirement by transitioning reviewed to True.
    """
    repo = SummaryRepository(db)
    updated = await repo.update_physician_review(session_id, edit_data)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case summary not found")
    return updated
