"""
Summary & FHIR Database Repository
==================================

File Purpose:
-------------
Encapsulates database operations for clinical case summaries (`case_summaries` table)
and standardized ABDM FHIR exports (`fhir_exports` table).

What it does:
-------------
1. Stores the initial AI-drafted case summary for a session.
2. Updates case summary with physician edits, diagnosis, and signs off (`reviewed = True`).
3. Saves and retrieves generated ABDM FHIR JSON bundles.
"""

import uuid
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.summary import CaseSummaryModel
from ..models.fhir import FHIRExportModel
from ..schemas.summary import PhysicianSummaryEditRequest


class SummaryRepository:
    """
    Database access layer for clinical summaries and FHIR exports.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_session_id(self, session_id: str) -> Optional[CaseSummaryModel]:
        """
        Fetch existing case summary record for a session.
        """
        stmt = select(CaseSummaryModel).where(CaseSummaryModel.session_id == session_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def save_ai_summary(
        self,
        session_id: str,
        chief_complaint: str,
        hpi: str,
        ai_draft_text: str,
        past_history: Optional[str] = None,
        current_medications: Optional[str] = None
    ) -> CaseSummaryModel:
        """
        Save or update the initial AI-generated case note draft.
        """
        existing = await self.get_by_session_id(session_id)
        if existing:
            existing.chief_complaint = chief_complaint
            existing.hpi = hpi
            existing.ai_draft_text = ai_draft_text
            existing.past_history = past_history
            existing.current_medications = current_medications
            existing.reviewed = False  # Reset reviewed if regenerated
            await self.db.flush()
            return existing

        new_summary = CaseSummaryModel(
            id=str(uuid.uuid4()),
            session_id=session_id,
            chief_complaint=chief_complaint,
            hpi=hpi,
            past_history=past_history,
            current_medications=current_medications,
            ai_draft_text=ai_draft_text,
            reviewed=False,
            disclaimer="AI-drafted. Physician review required before use."
        )
        self.db.add(new_summary)
        await self.db.flush()
        await self.db.refresh(new_summary)
        return new_summary

    async def update_physician_review(
        self,
        session_id: str,
        edit_data: PhysicianSummaryEditRequest
    ) -> Optional[CaseSummaryModel]:
        """
        Update the summary with physician verification, edits, and final sign-off.
        """
        summary = await self.get_by_session_id(session_id)
        if not summary:
            return None

        summary.physician_edited_text = edit_data.physician_edited_text
        summary.clinical_assessment = edit_data.clinical_assessment
        summary.reviewed = edit_data.reviewed
        summary.reviewed_by_doctor_id = edit_data.doctor_id
        summary.reviewed_at = datetime.now(timezone.utc)

        await self.db.flush()
        await self.db.refresh(summary)
        return summary

    async def save_fhir_export(
        self,
        session_id: str,
        fhir_json_str: str,
        status: str = "MOCKED"
    ) -> FHIRExportModel:
        """
        Save or update the generated FHIR JSON bundle export record.
        """
        stmt = select(FHIRExportModel).where(FHIRExportModel.session_id == session_id)
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            existing.fhir_json_payload = fhir_json_str
            existing.status = status
            await self.db.flush()
            return existing

        new_export = FHIRExportModel(
            id=str(uuid.uuid4()),
            session_id=session_id,
            fhir_resource_type="Bundle",
            fhir_json_payload=fhir_json_str,
            status=status,
            abdm_care_context_id=f"CARE_CTX_{session_id[:8]}"
        )
        self.db.add(new_export)
        await self.db.flush()
        await self.db.refresh(new_export)
        return new_export

    async def get_fhir_export(self, session_id: str) -> Optional[FHIRExportModel]:
        """
        Fetch FHIR export record by session ID.
        """
        stmt = select(FHIRExportModel).where(FHIRExportModel.session_id == session_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
