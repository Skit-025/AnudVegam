"""
Session Database Repository
===========================

File Purpose:
-------------
Encapsulates all database operations for intake sessions and Q&A history responses.

What it does:
-------------
1. Creates and manages session lifecycles (ACTIVE -> SCANNING -> SUMMARIZING -> REVIEWED).
2. Appends sequential interview Q&A responses into `history_responses`.
3. Loads full session aggregates (patient, responses, documents, entities, summary).
"""

import uuid
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from ..models.session import SessionModel
from ..models.response import HistoryResponseModel
from ..models.document import DocumentModel
from ..schemas.response import AnswerSubmissionRequest


class SessionRepository:
    """
    Database access layer for case-taking sessions and interview responses.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(self, patient_id: str, mode: str = "ALLOPATHIC") -> SessionModel:
        """
        Start a new case-taking session.
        """
        new_session = SessionModel(
            id=str(uuid.uuid4()),
            patient_id=patient_id,
            mode=mode.upper(),
            status="ACTIVE"
        )
        self.db.add(new_session)
        await self.db.flush()
        await self.db.refresh(new_session)
        return new_session

    async def get_session_by_id(self, session_id: str) -> Optional[SessionModel]:
        """
        Fetch session with eagerly loaded relations for doctor review.
        """
        stmt = (
            select(SessionModel)
            .where(SessionModel.id == session_id)
            .options(
                selectinload(SessionModel.patient),
                selectinload(SessionModel.responses),
                selectinload(SessionModel.documents).selectinload(DocumentModel.entities),
                selectinload(SessionModel.summary),
                selectinload(SessionModel.fhir_export)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def add_response(
        self,
        session_id: str,
        submission: AnswerSubmissionRequest,
        sequence_order: Optional[int] = None,
        is_red_flag: bool = False,
        red_flag_reason: Optional[str] = None
    ) -> HistoryResponseModel:
        """
        Append a patient Q&A answer turn to the database.
        """
        if sequence_order is None:
            stmt = select(func.coalesce(func.max(HistoryResponseModel.sequence_order), 0)).where(
                HistoryResponseModel.session_id == session_id
            )
            max_seq = (await self.db.execute(stmt)).scalar() or 0
            sequence_order = max_seq + 1

        new_resp = HistoryResponseModel(
            id=str(uuid.uuid4()),
            session_id=session_id,
            sequence_order=sequence_order,
            question_key=submission.question_key,
            question_text=submission.question_text,
            answer_text=submission.answer_text,
            input_mode=submission.input_mode,
            is_red_flag=is_red_flag,
            red_flag_reason=red_flag_reason
        )
        self.db.add(new_resp)
        await self.db.flush()
        await self.db.refresh(new_resp)
        return new_resp

    async def get_responses_for_session(self, session_id: str) -> List[HistoryResponseModel]:
        """
        Retrieve all ordered Q&A responses for a given session.
        """
        stmt = (
            select(HistoryResponseModel)
            .where(HistoryResponseModel.session_id == session_id)
            .order_by(HistoryResponseModel.sequence_order.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_status(self, session_id: str, new_status: str) -> Optional[SessionModel]:
        """
        Update the lifecycle status of an encounter session.
        """
        stmt = select(SessionModel).where(SessionModel.id == session_id)
        result = await self.db.execute(stmt)
        session = result.scalar_one_or_none()
        if session:
            session.status = new_status
            await self.db.flush()
        return session
