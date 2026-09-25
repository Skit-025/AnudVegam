"""
OCR AI Microservice - Main FastAPI Application
==============================================

File Purpose:
-------------
Entry point for the OCR AI microservice. Exposes HTTP endpoints for receiving medical
document uploads (prescriptions, lab reports) and returning recognized text and parsed entities.

What it does:
-------------
1. Configures FastAPI application, CORS middleware, and multipart file upload handling.
2. Exposes `/health` and `/api/ocr/extract` endpoints.
3. Delegates document bytes to `OCRPipelineService`.

Connected to:
-------------
- `ai-services/ocr/app/services/ocr_service.py`: Dispatches document processing.
- `ai-services/ocr/app/schemas/ocr.py`: Response schema serialization.
- `backend/app/clients/ocr_client.py`: Upstream caller from Main Backend.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from .schemas.ocr import OCRProcessingResult
from .services.ocr_service import OCRPipelineService

app = FastAPI(
    title="MediKiosk OCR AI Service",
    version="1.0.0",
    description="Medical document image preprocessing, Tesseract OCR, and clinical entity extraction service"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ocr_service = OCRPipelineService()


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify OCR service status and Tesseract availability.

    Returns:
    --------
    dict: Service status indicator.
    """
    # Step 1: Check Tesseract binary availability.
    # Step 2: Return status OK.
    return {"status": "healthy", "service": "ocr-ai"}


@app.post(
    "/api/ocr/extract",
    response_model=OCRProcessingResult,
    status_code=status.HTTP_200_OK,
    tags=["OCR"]
)
async def extract_document_entities(file: UploadFile = File(...)):
    """
    Upload a prescription or lab report image, execute image preprocessing, OCR,
    and structured entity extraction.

    Parameters:
    -----------
    file: UploadFile
        Multipart image payload (PNG, JPEG, PDF).

    Returns:
    --------
    OCRProcessingResult:
        Raw OCR text, list of extracted medical entities, and processing metadata.
    """
    # Step 1: Validate file content type (image/png, image/jpeg, application/pdf).
    # Step 2: Read file bytes into memory.
    # Step 3: Pass image bytes to ocr_service.process_document(image_bytes).
    # Step 4: Return populated OCRProcessingResult model.
    contents = await file.read()
    return ocr_service.process_document(contents)
