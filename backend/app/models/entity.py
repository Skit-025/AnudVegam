"""
Extracted Entity ORM Model (`extracted_entities` table)
=======================================================

File Purpose:
-------------
Stores structured clinical entities parsed from scanned document OCR text.

What it does:
-------------
1. Stores parsed entities: medicines, dosages, lab tests, quantitative lab values, dates, diagnoses.
2. Tracks abnormality indicators for lab tests outside reference ranges.
3. Associates each entity with its source document and session for auditability.

Connected to:
-------------
- `backend/app/models/document.py`: Belongs to `DocumentModel`.
- `backend/app/clients/ocr_client.py`: Populated from OCR AI extraction payload.
- `backend/app/clients/summarizer_client.py`: Transmitted to Summarizer AI to formulate clinical notes.
"""

import uuid
from typing import Optional
from sqlalchemy import String, Float, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin


class ExtractedEntityModel(Base, TimestampMixin):
    """
    SQLAlchemy model representing the 'extracted_entities' database table.
    """
    __tablename__ = "extracted_entities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False)  # MEDICINE, LAB_VALUE, DATE, DIAGNOSIS
    entity_value: Mapped[str] = mapped_column(String(255), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    is_abnormal: Mapped[bool] = mapped_column(Boolean, default=False)
    reference_range: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Relationships
    document: Mapped["DocumentModel"] = relationship("DocumentModel", back_populates="entities")
