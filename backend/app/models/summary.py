"""
Case Summary ORM Model (`case_summaries` table)
===============================================

File Purpose:
-------------
Stores the AI-generated draft case summary and subsequent physician edits, review status,
and clinical sign-off records.

What it does:
-------------
1. Stores the initial AI-drafted clinical summary text.
2. Captures physician edits, assessments, and provisional diagnosis.
3. Maintains human-in-the-loop review state (`reviewed = True/False`).
4. Enforces the permanent audit record of who reviewed the case and when.

Connected to:
-------------
- `backend/app/models/session.py`: Belongs to `SessionModel` (1:1).
- `backend/app/clients/summarizer_client.py`: Initial draft received from Summarizer AI.
- `backend/app/api/summaries.py`: Updated when doctor saves edits or confirms review.
- `backend/app/services/fhir_exporter.py`: Used as primary source for FHIR Composition.
"""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin


class CaseSummaryModel(Base, TimestampMixin):
    """
    SQLAlchemy model representing the 'case_summaries' database table.
    """
    __tablename__ = "case_summaries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), unique=True, index=True)
    chief_complaint: Mapped[str] = mapped_column(Text, nullable=False)
    hpi: Mapped[str] = mapped_column(Text, nullable=False)
    past_history: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    current_medications: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON or comma-separated
    ai_draft_text: Mapped[str] = mapped_column(Text, nullable=False)
    physician_edited_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    clinical_assessment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reviewed_by_doctor_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    disclaimer: Mapped[str] = mapped_column(
        String(255),
        default="AI-drafted. Physician review required before use."
    )

    # Relationships
    session: Mapped["SessionModel"] = relationship("SessionModel", back_populates="summary")
