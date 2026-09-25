"""
Summarizer AI Microservice - Main FastAPI Application
=====================================================

File Purpose:
-------------
Entry point for the Summarizer AI microservice. Exposes HTTP endpoints for receiving
patient intake history and OCR data, and returning structured clinical note drafts.

What it does:
-------------
1. Configures FastAPI application and CORS middleware.
2. Exposes `/health` and `/api/summarizer/generate` endpoints.
3. Delegates summary compilation to `CaseSummaryPipelineService`.

Connected to:
-------------
- `ai-services/summarizer/app/services/summary_service.py`: Executes case note generation.
- `ai-services/summarizer/app/schemas/summary.py`: Request and response schemas.
- `backend/app/clients/summarizer_client.py`: Upstream caller from Main Backend.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from .schemas.summary import SummaryGenerationRequest, StructuredClinicalSummary
from .services.summary_service import CaseSummaryPipelineService

app = FastAPI(
    title="MediKiosk Summarizer AI Service",
    version="1.0.0",
    description="Clinical case note generation service using prompt-engineered LLM pipelines"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

summary_service = CaseSummaryPipelineService()


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify Summarizer service and LLM connectivity.

    Returns:
    --------
    dict: Service status indicator.
    """
    # Step 1: Verify service uptime and LLM provider connectivity.
    # Step 2: Return status OK.
    return {"status": "healthy", "service": "summarizer-ai"}


@app.post(
    "/api/summarizer/generate",
    response_model=StructuredClinicalSummary,
    status_code=status.HTTP_200_OK,
    tags=["Summarizer"]
)
async def generate_case_summary(request: SummaryGenerationRequest):
    """
    Synthesize structured patient interview responses and OCR document entities
    into an editable clinical case-note draft.

    Parameters:
    -----------
    request: SummaryGenerationRequest
        Patient context, interview Q&A list, and extracted OCR entities.

    Returns:
    --------
    StructuredClinicalSummary:
        Sectioned case note draft with mandatory AI disclaimer and reviewed=False.
    """
    # Step 1: Validate incoming request via Pydantic model.
    # Step 2: Call summary_service.generate_summary(request).
    # Step 3: Handle LLM API timeouts or offline exceptions gracefully.
    # Step 4: Return populated StructuredClinicalSummary.
    return await summary_service.generate_summary(request)
