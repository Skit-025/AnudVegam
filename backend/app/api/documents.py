"""
Documents API Router
====================

File Purpose:
-------------
Exposes HTTP endpoints for handling scanned document uploads (prescriptions, lab tests)
at the kiosk terminal and triggering the OCR AI microservice.

Endpoints:
----------
- `POST /api/sessions/{id}/documents`: Upload document image, run OCR and entity extraction in real time.

Connected to:
-------------
- `backend/app/clients/ocr_client.py`: Forwards file bytes to OCR microservice.
- `backend/app/repositories/document_repo.py`: Persists document record and extracted entities.
- `backend/app/schemas/document.py`: Serializes upload response.
"""

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.dependencies import get_db, get_ocr_client
from ..schemas.document import DocumentResponseItem, ExtractedEntityItem
from ..repositories.document_repo import DocumentRepository
from ..clients.ocr_client import OCRClient

router = APIRouter(prefix="/api/sessions", tags=["Documents"])


@router.post(
    "/{session_id}/documents",
    response_model=DocumentResponseItem,
    status_code=status.HTTP_201_CREATED,
    summary="Upload document and invoke OCR service"
)
async def upload_document(
    session_id: str,
    file: UploadFile = File(...),
    document_type: str = Form("PRESCRIPTION"),
    db: AsyncSession = Depends(get_db),
    ocr_client: OCRClient = Depends(get_ocr_client)
):
    """
    Accept an uploaded prescription or lab report image, call the OCR microservice
    for OpenCV preprocessing and Tesseract entity extraction, and save results in real time.
    """
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")

    # 1. Run real OCR and entity extraction
    ocr_result = await ocr_client.extract_document_entities(
        contents,
        file.filename or "prescription.jpg",
        file.content_type or "image/jpeg"
    )

    # 2. Persist document in database
    repo = DocumentRepository(db)
    doc = await repo.create_document(
        session_id=session_id,
        file_name=file.filename or "scanned_doc.jpg",
        file_path=f"storage/{session_id}/{file.filename or 'doc.jpg'}",
        document_type=document_type,
        raw_ocr_text=ocr_result.get("raw_text", "")
    )

    # 3. Batch persist extracted entities in database
    extracted_entities_data = ocr_result.get("entities", [])
    saved_entity_models = await repo.add_extracted_entities(doc.id, extracted_entities_data)

    # 4. Format response
    entity_items = [
        ExtractedEntityItem(
            id=ent.id,
            entity_type=ent.entity_type,
            entity_value=ent.entity_value,
            confidence=ent.confidence,
            is_abnormal=ent.is_abnormal,
            reference_range=ent.reference_range
        )
        for ent in saved_entity_models
    ]

    return DocumentResponseItem(
        id=doc.id,
        file_name=doc.file_name,
        document_type=doc.document_type,
        raw_ocr_text=doc.raw_ocr_text,
        entities=entity_items,
        created_at=doc.created_at
    )
