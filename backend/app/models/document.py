"""
Document ORM Model (`documents` table)
======================================

File Purpose:
-------------
Represents scanned medical prescriptions, lab reports, and clinical records uploaded at the kiosk.

What it does:
-------------
1. Stores file storage paths, mime types, and document classification (PRESCRIPTION, LAB_REPORT).
2. Retains complete raw OCR text returned by the OCR AI microservice.
3. Maintains one-to-many relationship with structured entities extracted from this document.

Connected to:
-------------
- `backend/app/models/session.py`: Belongs to `SessionModel`.
- `backend/app/models/entity.py`: Has many `ExtractedEntityModel`.
- `backend/app/clients/ocr_client.py`: Dispatched for image preprocessing and Tesseract recognition.
"""

import uuid
from typing import List, Optional
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin


class DocumentModel(Base, TimestampMixin):
    """
    SQLAlchemy model representing the 'documents' database table.
    """
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    document_type: Mapped[str] = mapped_column(String(32), default="PRESCRIPTION")  # PRESCRIPTION, LAB_REPORT
    raw_ocr_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    session: Mapped["SessionModel"] = relationship("SessionModel", back_populates="documents")
    entities: Mapped[List["ExtractedEntityModel"]] = relationship(
        "ExtractedEntityModel", back_populates="document", cascade="all, delete-orphan"
    )
