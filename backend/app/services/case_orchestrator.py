"""
Main Backend - Patient Case-Taking Orchestrator Service
======================================================

File Purpose:
-------------
Acts as the central business logic controller for the entire MediKiosk backend.
Orchestrates the lifecycle of patient case-taking:
- Starting sessions
- Coordinating Q&A interview turns with the Dialogue AI service
- Delegating scanned files to the OCR AI service
- Aggregating context to invoke the Summarizer AI service
- Persisting state across PostgreSQL / SQLite tables in real time

What it does:
-------------
1. Enforces the sequential progression of kiosk screens (Identify -> Converse -> Scan -> Summary -> Consult).
2. Propagates medical red-flag markers detected during interview questions.
3. Packages composite context for LLM summarization.
4. Ensures the safety rule: AI summaries are saved with `reviewed = False` and mandatory disclaimers.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from ..repositories.session_repo import SessionRepository
from ..repositories.patient_repo import PatientRepository
from ..repositories.document_repo import DocumentRepository
from ..repositories.summary_repo import SummaryRepository
from ..clients.dialogue_client import DialogueClient
from ..clients.ocr_client import OCRClient
from ..clients.summarizer_client import SummarizerClient
from ..schemas.response import AnswerSubmissionRequest


class CaseOrchestratorService:
    """
    Core business logic orchestrator for patient case-taking and multi-service AI coordination.
    """

    def __init__(
        self,
        db: AsyncSession,
        dialogue_client: DialogueClient,
        ocr_client: OCRClient,
        summarizer_client: SummarizerClient
    ):
        self.db = db
        self.session_repo = SessionRepository(db)
        self.patient_repo = PatientRepository(db)
        self.doc_repo = DocumentRepository(db)
        self.summary_repo = SummaryRepository(db)
        self.dialogue_client = dialogue_client
        self.ocr_client = ocr_client
        self.summarizer_client = summarizer_client

    async def get_next_question_for_session(self, session_id: str) -> Dict[str, Any]:
        """
        Fetch previous Q&A turns, determine language and mode, and call Dialogue AI for next prompt in real time.
        """
        session = await self.session_repo.get_session_by_id(session_id)
        if not session:
            raise ValueError(f"Session with ID {session_id} not found.")

        language = session.patient.preferred_language if session.patient else "en"
        mode = session.mode or "ALLOPATHIC"

        # Format historical answers
        previous_answers = [
            {
                "question_key": resp.question_key,
                "answer_text": resp.answer_text,
                "input_mode": resp.input_mode
            }
            for resp in session.responses
        ]

        # Call Dialogue AI microservice
        next_q = await self.dialogue_client.fetch_next_question(
            session_id=session_id,
            mode=mode,
            language=language,
            previous_answers=previous_answers
        )

        # Advance session status to SCANNING if questions are complete
        if next_q.get("is_final", False):
            await self.session_repo.update_status(session_id, "SCANNING")

        return next_q

    async def submit_patient_answer(
        self,
        session_id: str,
        submission: AnswerSubmissionRequest
    ) -> Dict[str, Any]:
        """
        Record patient's answer turn, evaluate for red flags via Dialogue AI, and advance session.
        """
        session = await self.session_repo.get_session_by_id(session_id)
        if not session:
            raise ValueError(f"Session with ID {session_id} not found.")

        mode = session.mode or "ALLOPATHIC"
        language = session.patient.preferred_language if session.patient else "en"

        # Evaluate red flags for this response
        q_payload = await self.dialogue_client.fetch_next_question(
            session_id=session_id,
            mode=mode,
            language=language,
            previous_answers=[{"question_key": submission.question_key, "answer_text": submission.answer_text, "input_mode": submission.input_mode}]
        )
        red_flag_data = q_payload.get("red_flag", {})
        is_red_flag = red_flag_data.get("detected", False)
        red_flag_reason = red_flag_data.get("reason")

        # Save response in database
        saved_resp = await self.session_repo.add_response(
            session_id=session_id,
            submission=submission,
            is_red_flag=is_red_flag,
            red_flag_reason=red_flag_reason
        )

        return {
            "id": saved_resp.id,
            "session_id": session_id,
            "sequence_order": saved_resp.sequence_order,
            "question_key": saved_resp.question_key,
            "is_red_flag": is_red_flag,
            "red_flag_reason": red_flag_reason,
            "status": "SAVED"
        }

    async def trigger_case_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Gather patient profile, Q&A interview responses, and OCR extracted entities,
        then invoke Summarizer AI to draft clinical case note in real time.
        """
        session = await self.session_repo.get_session_by_id(session_id)
        if not session:
            raise ValueError(f"Session with ID {session_id} not found.")

        # Prepare patient demographic context
        patient_ctx = {
            "name": session.patient.name if session.patient else "Unknown",
            "age": session.patient.age if session.patient else 30,
            "gender": session.patient.gender if session.patient else "MALE",
            "preferred_language": session.patient.preferred_language if session.patient else "en"
        }

        # Prepare Q&A history
        responses_payload = [
            {
                "question_key": r.question_key,
                "question_text": r.question_text,
                "answer_text": r.answer_text
            }
            for r in session.responses
        ]

        # Prepare OCR entities
        entities_list = await self.doc_repo.get_entities_by_session(session_id)
        entities_payload = [
            {
                "entity_type": e.entity_type,
                "entity_value": e.entity_value,
                "is_abnormal": e.is_abnormal
            }
            for e in entities_list
        ]

        summary_req = {
            "session_id": session_id,
            "mode": session.mode or "ALLOPATHIC",
            "patient": patient_ctx,
            "responses": responses_payload,
            "extracted_entities": entities_payload
        }

        # Call Summarizer AI microservice
        ai_summary = await self.summarizer_client.generate_case_summary(summary_req)

        # Save AI draft to database
        saved_summary = await self.summary_repo.save_ai_summary(
            session_id=session_id,
            chief_complaint=ai_summary.get("chief_complaint", "General consultation"),
            hpi=ai_summary.get("hpi", "Clinical intake recorded."),
            ai_draft_text=ai_summary.get("raw_ai_draft", "AI-drafted note."),
            past_history=ai_summary.get("past_history"),
            current_medications=", ".join(ai_summary.get("current_medications", []))
        )

        # Update session status
        await self.session_repo.update_status(session_id, "SUMMARIZED")

        return {
            "id": saved_summary.id,
            "session_id": session_id,
            "chief_complaint": saved_summary.chief_complaint,
            "hpi": saved_summary.hpi,
            "past_history": saved_summary.past_history,
            "current_medications": saved_summary.current_medications,
            "ai_draft_text": saved_summary.ai_draft_text,
            "physician_edited_text": saved_summary.physician_edited_text,
            "clinical_assessment": saved_summary.clinical_assessment,
            "reviewed": saved_summary.reviewed,
            "disclaimer": saved_summary.disclaimer,
            "created_at": saved_summary.created_at
        }
