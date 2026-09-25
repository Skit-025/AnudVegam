"""
OCR Service Data Schemas
========================

File Purpose:
-------------
Defines the Pydantic data schemas used for prescription/lab report OCR processing,
raw text representation, and extracted clinical entity structures.

What it does:
-------------
1. Validates document processing metadata and image upload parameters.
2. Defines structured models for extracted medical entities (medicines, lab values, dates, diagnoses).
3. Formats the full OCR response delivered back to the Main Backend.

Connected to:
-------------
- `ai-services/ocr/app/extraction/entity_extractor.py`: Uses `ExtractedEntity` and `ExtractedEntityList`.
- `ai-services/ocr/app/services/ocr_service.py`: Uses `OCRProcessingResult` as output format.
- `ai-services/ocr/app/main.py`: Uses schemas in route response definitions.
- `backend/app/clients/ocr_client.py`: Deserializes these models in the main backend.
- `backend/app/models/entity.py`: Maps directly to the PostgreSQL `extracted_entities` table.
"""

from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class EntityType(str, Enum):
    """Categorization of clinical entities extracted from medical documents."""
    MEDICINE = "MEDICINE"
    DOSAGE = "DOSAGE"
    LAB_TEST = "LAB_TEST"
    LAB_VALUE = "LAB_VALUE"
    DIAGNOSIS = "DIAGNOSIS"
    DOCUMENT_DATE = "DOCUMENT_DATE"
    DOCTOR_NAME = "DOCTOR_NAME"


class ExtractedEntity(BaseModel):
    """
    Represents an individual clinical entity parsed from raw OCR text.
    """
    entity_type: EntityType = Field(..., description="Classification of the entity")
    entity_value: str = Field(..., description="Extracted text string (e.g., 'Paracetamol 500mg')")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Extraction confidence score (0.0-1.0)")
    is_abnormal: bool = Field(default=False, description="Flag if a lab value falls outside normal reference intervals")
    reference_range: Optional[str] = Field(default=None, description="Normal reference range if detected on lab report")


class OCRProcessingResult(BaseModel):
    """
    Complete response returned by the OCR AI service after processing an uploaded document.
    """
    raw_text: str = Field(..., description="Full machine-readable text recognized by Tesseract OCR")
    entities: List[ExtractedEntity] = Field(default_factory=list, description="List of structured clinical entities")
    page_count: int = Field(default=1, description="Number of document pages scanned")
    preprocessing_applied: List[str] = Field(
        default_factory=list,
        description="List of computer vision operations performed (e.g., deskew, contrast adjustment)"
    )
