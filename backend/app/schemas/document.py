"""
Document & Entity Pydantic Schemas
==================================

File Purpose:
-------------
Defines request and response schemas for uploaded medical documents (prescriptions,
reports) and their extracted clinical entities.

Connected to:
-------------
- `backend/app/api/documents.py`: File upload response schema.
- `backend/app/models/document.py` & `entity.py`: Maps ORM models to API serialization.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ExtractedEntityItem(BaseModel):
    """Structured clinical entity item."""
    id: str
    entity_type: str
    entity_value: str
    confidence: float
    is_abnormal: bool
    reference_range: Optional[str] = None

    class Config:
        from_attributes = True


class DocumentResponseItem(BaseModel):
    """Scanned document record and associated extracted entities."""
    id: str
    file_name: str
    document_type: str
    raw_ocr_text: Optional[str] = None
    entities: List[ExtractedEntityItem] = Field(default_factory=list)
    created_at: datetime

    class Config:
        from_attributes = True
