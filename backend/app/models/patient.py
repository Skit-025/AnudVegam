"""
Patient ORM Model (`patients` table)
====================================

File Purpose:
-------------
Represents registered or identified patients visiting the MediKiosk.

What it does:
-------------
1. Stores patient identity (mock ABHA address, Aadhaar token, internal UUID).
2. Holds demographics: full name, age, gender, contact number, preferred language.
3. Maintains one-to-many relationships with consents and case-taking sessions.

Connected to:
-------------
- `backend/app/models/consent.py`: One-to-many relationship with `ConsentModel`.
- `backend/app/models/session.py`: One-to-many relationship with `SessionModel`.
- `backend/app/repositories/patient_repo.py`: Queried and mutated by patient repository.
- `backend/app/schemas/patient.py`: Validated against Pydantic schemas.
"""

import uuid
from typing import List, Optional
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin


class PatientModel(Base, TimestampMixin):
    """
    SQLAlchemy model representing the 'patients' database table.
    """
    __tablename__ = "patients"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    abha_id: Mapped[Optional[str]] = mapped_column(String(32), unique=True, index=True, nullable=True)
    aadhaar_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(16), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    preferred_language: Mapped[str] = mapped_column(String(8), default="en")

    # Relationships
    consents: Mapped[List["ConsentModel"]] = relationship("ConsentModel", back_populates="patient", cascade="all, delete-orphan")
    sessions: Mapped[List["SessionModel"]] = relationship("SessionModel", back_populates="patient", cascade="all, delete-orphan")
