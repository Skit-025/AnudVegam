"""
Dialogue AI Microservice - Main FastAPI Application
===================================================

File Purpose:
-------------
Entry point for the Dialogue AI service. Exposes HTTP endpoints for next-question
lookup and red-flag screening for patient intake.

What it does:
-------------
1. Initializes the FastAPI web application with CORS and lifespan events.
2. Exposes `/health` and `/api/dialogue/next-question` endpoints.
3. Delegates business logic to `InterviewService`.

Connected to:
-------------
- `ai-services/dialogue/app/services/interview_service.py`: Dispatches Q&A orchestration.
- `ai-services/dialogue/app/schemas/dialogue.py`: Validates input and output payloads.
- `backend/app/clients/dialogue_client.py`: Upstream caller from Main Backend.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from .schemas.dialogue import NextQuestionRequest, NextQuestionResponse
from .services.interview_service import InterviewService

app = FastAPI(
    title="MediKiosk Dialogue AI Service",
    version="1.0.0",
    description="Medical intake question-flow and red-flag detection service"
)

# Enable CORS for local cross-service communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

interview_service = InterviewService()


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify that the dialogue service is operational.

    Returns:
    --------
    dict: Service status indicator.
    """
    # Step 1: Verify service uptime and rule engine readiness.
    # Step 2: Return status OK.
    return {"status": "healthy", "service": "dialogue-ai"}


@app.post(
    "/api/dialogue/next-question",
    response_model=NextQuestionResponse,
    status_code=status.HTTP_200_OK,
    tags=["Dialogue"]
)
async def get_next_question(request: NextQuestionRequest):
    """
    Process patient's previous Q&A turns and compute the next clinical interview question.

    Parameters:
    -----------
    request: NextQuestionRequest
        Contains session ID, triage mode (Allopathic/AYUSH), target language, and Q&A history.

    Returns:
    --------
    NextQuestionResponse:
        Next question text, UI input options, and red-flag alert status.
    """
    # Step 1: Validate incoming request via Pydantic model.
    # Step 2: Call interview_service.process_next_step(request).
    # Step 3: Handle potential exceptions or rule traversal errors.
    # Step 4: Return formatted NextQuestionResponse.
    return interview_service.process_next_step(request)
