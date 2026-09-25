"""
Session ORM Model (`sessions` table)
====================================

File Purpose:
-------------
Represents an active or completed patient case-taking encounter at the kiosk terminal.

What it does:
-------------
1. Tracks session lifecycle status (ACTIVE, QUESTIONING, SCANNING, SUMMARIZING, REVIEWED, EXPORTED).
2. Distinguishes clinical department intake mode (ALLOPATHIC or AYUSH).
3. Connects history responses, uploaded documents, clinical summary, and FHIR export.

Connected to:
-------------
- `backend/app/models/patient.py`: Belongs to `PatientModel`.
- `backend/app/models/response.py`: Has many `HistoryResponseModel`.
- `backend/app/models/document.py`: Has many `DocumentModel`.
- `backend/app/models/summary.py`: Has one `CaseSummaryModel`.
- `backend/app/models/fhir.py`: Has one `FHIRExportModel`.
"""

import uuid
from typing import List, Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin


class SessionModel(Base, TimestampMixin):
    """
    SQLAlchemy model representing the 'sessions' database table.
    """
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), index=True)
    mode: Mapped[str] = mapped_column(String(20), default="ALLOPATHIC")  # ALLOPATHIC or AYUSH
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE")    # ACTIVE, COMPLETED, REVIEWED
    assigned_doctor_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Relationships
    patient: Mapped["PatientModel"] = relationship("PatientModel", back_populates="sessions")
    responses: Mapped[List["HistoryResponseModel"]] = relationship(
        "HistoryResponseModel", back_populates="session", cascade="all, delete-orphan", order_by="HistoryResponseModel.sequence_order"
    )
    documents: Mapped[List["DocumentModel"]] = relationship(
        "DocumentModel", back_populates="session", cascade="all, delete-orphan"
    )
    summary: Mapped[Optional["CaseSummaryModel"]] = relationship(
        "CaseSummaryModel", back_populates="session", uselist=False, cascade="all, delete-orphan"
    )
    fhir_export: Mapped[Optional["FHIRExportModel"]] = relationship(
        "FHIRExportModel", back_populates="session", uselist=False, cascade="all, delete-orphan"
    )
