"""
Patient Database Repository
===========================

File Purpose:
-------------
Encapsulates all database query and mutation operations for the `patients` and `consents` tables.

What it does:
-------------
1. Creates new patient records or retrieves existing patients by ABHA ID or internal UUID.
2. Persists and queries patient informed consent records.
3. Provides clean async DB operations for route handlers and services.
"""

import uuid
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.patient import PatientModel
from ..models.consent import ConsentModel
from ..schemas.patient import PatientCreate
from ..schemas.consent import ConsentGrantRequest


class PatientRepository:
    """
    Database access layer for patient demographics and consent records.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, patient_id: str) -> Optional[PatientModel]:
        """
        Fetch patient by internal UUID.
        """
        stmt = select(PatientModel).where(PatientModel.id == patient_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_abha_id(self, abha_id: str) -> Optional[PatientModel]:
        """
        Lookup patient by their 14-digit ABHA identifier.
        """
        stmt = select(PatientModel).where(PatientModel.abha_id == abha_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, patient_data: PatientCreate) -> PatientModel:
        """
        Create or return existing patient in PostgreSQL/SQLite.
        """
        if patient_data.abha_id:
            existing = await self.get_by_abha_id(patient_data.abha_id)
            if existing:
                # Update language or phone if changed
                existing.preferred_language = patient_data.preferred_language
                if patient_data.phone:
                    existing.phone = patient_data.phone
                await self.db.flush()
                return existing

        new_patient = PatientModel(
            id=str(uuid.uuid4()),
            abha_id=patient_data.abha_id,
            name=patient_data.name,
            age=patient_data.age,
            gender=patient_data.gender,
            phone=patient_data.phone,
            preferred_language=patient_data.preferred_language
        )
        self.db.add(new_patient)
        await self.db.flush()
        await self.db.refresh(new_patient)
        return new_patient

    async def record_consent(self, consent_data: ConsentGrantRequest) -> ConsentModel:
        """
        Save patient consent agreement to the database.
        """
        new_consent = ConsentModel(
            id=str(uuid.uuid4()),
            patient_id=consent_data.patient_id,
            consent_granted=consent_data.consent_granted,
            consent_text=consent_data.consent_text,
            language=consent_data.language
        )
        self.db.add(new_consent)
        await self.db.flush()
        await self.db.refresh(new_consent)
        return new_consent
