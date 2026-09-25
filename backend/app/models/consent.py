"""
Consent ORM Model (`consents` table)
====================================

File Purpose:
-------------
Maintains legally binding informed consent records for digital case-taking and AI drafting.

What it does:
-------------
1. Stores the exact consent disclaimer text agreed to by the patient on the kiosk screen.
2. Tracks consent status (granted/revoked), language used, and precise timestamp.
3. Associates consent records with the respective patient.

Connected to:
-------------
- `backend/app/models/patient.py`: Belongs to `PatientModel`.
- `backend/app/api/consents.py`: Persisted via consent endpoint.
- `backend/app/schemas/consent.py`: Serialized/deserialized with Pydantic.
"""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin


class ConsentModel(Base, TimestampMixin):
    """
    SQLAlchemy model representing the 'consents' database table.
    """
    __tablename__ = "consents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), index=True)
    consent_granted: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    consent_text: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(8), default="en")
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    patient: Mapped["PatientModel"] = relationship("PatientModel", back_populates="consents")
