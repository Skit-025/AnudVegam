"""
Sessions API Router
===================

File Purpose:
-------------
Exposes HTTP endpoints for managing the core case-taking encounter lifecycle:
- Starting a new intake session (Allopathic / AYUSH)
- Fetching the next clinical question from Dialogue AI
- Submitting patient answers and checking red flags
- Fetching full session aggregates for physician review

Endpoints:
----------
- `POST /api/sessions`: Start new session.
- `GET /api/sessions/{id}/next-question`: Retrieve next interview question.
- `POST /api/sessions/{id}/responses`: Submit patient's answer turn.
- `GET /api/sessions/{id}`: Return full session details for doctor review.

Connected to:
-------------
- `backend/app/services/case_orchestrator.py`: Dispatches business logic and AI coordination.
- `backend/app/schemas/session.py` & `response.py`: Validates payloads.
- `backend/app/core/dependencies.py`: Injects DB, DialogueClient, OCRClient, SummarizerClient.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.dependencies import get_db, get_dialogue_client, get_ocr_client, get_summarizer_client
from ..schemas.session import SessionCreateRequest, SessionResponse, CompleteSessionDetail
from ..schemas.response import AnswerSubmissionRequest, HistoryResponseItem
from ..services.case_orchestrator import CaseOrchestratorService
from ..repositories.session_repo import SessionRepository
from ..clients.dialogue_client import DialogueClient
from ..clients.ocr_client import OCRClient
from ..clients.summarizer_client import SummarizerClient

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start new case-taking session"
)
async def start_session(
    request: SessionCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Initialize a new patient encounter in Allopathic or AYUSH triage mode.

    Parameters:
    -----------
    request: SessionCreateRequest
        Patient UUID and clinical mode.
    db: AsyncSession
        Injected async database session.

    Returns:
    --------
    SessionResponse:
        Created session with status ACTIVE.
    """
    # Step 1: Initialize SessionRepository.
    # Step 2: Validate that patient exists.
    # Step 3: Create session record with mode and status='ACTIVE'.
    # Step 4: Return SessionResponse.
    repo = SessionRepository(db)
    return await repo.create_session(request.patient_id, request.mode)


@router.get(
    "/{session_id}/next-question",
    summary="Get next question from Dialogue AI service"
)
async def get_next_question(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    dialogue_client: DialogueClient = Depends(get_dialogue_client),
    ocr_client: OCRClient = Depends(get_ocr_client),
    summarizer_client: SummarizerClient = Depends(get_summarizer_client)
):
    """
    Fetch the next interview question tailored to previous answers and clinical mode.

    Parameters:
    -----------
    session_id: str
        UUID of the active session.

    Returns:
    --------
    dict:
        Question payload (question_key, text, options, is_final, red_flag).
    """
    # Step 1: Instantiate CaseOrchestratorService.
    # Step 2: Call orchestrator.get_next_question_for_session(session_id).
    # Step 3: Return question response.
    orchestrator = CaseOrchestratorService(db, dialogue_client, ocr_client, summarizer_client)
    return await orchestrator.get_next_question_for_session(session_id)


@router.post(
    "/{session_id}/responses",
    summary="Submit one Q&A turn and evaluate red flags"
)
async def submit_response(
    session_id: str,
    submission: AnswerSubmissionRequest,
    db: AsyncSession = Depends(get_db),
    dialogue_client: DialogueClient = Depends(get_dialogue_client),
    ocr_client: OCRClient = Depends(get_ocr_client),
    summarizer_client: SummarizerClient = Depends(get_summarizer_client)
):
    """
    Record patient's response, evaluate red-flag rules, and update session history.

    Parameters:
    -----------
    session_id: str
        UUID of the active session.
    submission: AnswerSubmissionRequest
        Question key, text, answer text, and touch/voice input mode.

    Returns:
    --------
    dict:
        Saved response confirmation and detected red flags.
    """
    # Step 1: Instantiate CaseOrchestratorService.
    # Step 2: Call orchestrator.submit_patient_answer(session_id, submission).
    # Step 3: Return confirmation result.
    orchestrator = CaseOrchestratorService(db, dialogue_client, ocr_client, summarizer_client)
    return await orchestrator.submit_patient_answer(session_id, submission)


@router.get(
    "/{session_id}",
    response_model=CompleteSessionDetail,
    summary="Return complete session for doctor review"
)
async def get_session_detail(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch complete session details (patient demographics, Q&A history, uploaded documents,
    extracted entities, and draft/confirmed summary) for doctor consultation.

    Parameters:
    -----------
    session_id: str
        UUID of the session.

    Returns:
    --------
    CompleteSessionDetail:
        Full relational tree for physician review dashboard.
    """
    # Step 1: Query SessionRepository.get_session_by_id(session_id).
    # Step 2: If session not found, raise 404 HTTPException.
    # Step 3: Serialize into CompleteSessionDetail.
    # Step 4: Return complete session graph.
    repo = SessionRepository(db)
    session = await repo.get_session_by_id(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session
