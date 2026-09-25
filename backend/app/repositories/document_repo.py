"""
Document & Entity Database Repository
=====================================

File Purpose:
-------------
Encapsulates all database operations for scanned medical files (`documents` table)
and parsed clinical entities (`extracted_entities` table).

What it does:
-------------
1. Records uploaded document metadata and raw OCR text.
2. Batch inserts extracted clinical entities (medicines, lab values, dates) linked to the document.
3. Retrieves all document entities across a session to feed into the clinical summarizer.
"""

import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.document import DocumentModel
from ..models.entity import ExtractedEntityModel


class DocumentRepository:
    """
    Database access layer for uploaded medical records and OCR entities.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_document(
        self,
        session_id: str,
        file_name: str,
        file_path: str,
        document_type: str = "PRESCRIPTION",
        raw_ocr_text: Optional[str] = None
    ) -> DocumentModel:
        """
        Persist uploaded document metadata and raw OCR text.
        """
        doc = DocumentModel(
            id=str(uuid.uuid4()),
            session_id=session_id,
            file_name=file_name,
            file_path=file_path,
            document_type=document_type,
            raw_ocr_text=raw_ocr_text
        )
        self.db.add(doc)
        await self.db.flush()
        await self.db.refresh(doc)
        return doc

    async def add_extracted_entities(
        self,
        document_id: str,
        entities: List[Dict[str, Any]]
    ) -> List[ExtractedEntityModel]:
        """
        Batch save parsed clinical entities linked to the document.
        """
        saved_models = []
        for ent in entities:
            # ent can be ExtractedEntity schema or dict
            entity_type = ent.get("entity_type") if isinstance(ent, dict) else getattr(ent, "entity_type", "MEDICINE")
            entity_value = ent.get("entity_value") if isinstance(ent, dict) else getattr(ent, "entity_value", "")
            confidence = ent.get("confidence", 1.0) if isinstance(ent, dict) else getattr(ent, "confidence", 1.0)
            is_abnormal = ent.get("is_abnormal", False) if isinstance(ent, dict) else getattr(ent, "is_abnormal", False)
            reference_range = ent.get("reference_range") if isinstance(ent, dict) else getattr(ent, "reference_range", None)

            entity_model = ExtractedEntityModel(
                id=str(uuid.uuid4()),
                document_id=document_id,
                entity_type=str(entity_type),
                entity_value=str(entity_value),
                confidence=float(confidence),
                is_abnormal=bool(is_abnormal),
                reference_range=reference_range
            )
            self.db.add(entity_model)
            saved_models.append(entity_model)

        await self.db.flush()
        return saved_models

    async def get_entities_by_session(self, session_id: str) -> List[ExtractedEntityModel]:
        """
        Fetch all clinical entities parsed across all documents uploaded in a session.
        """
        stmt = (
            select(ExtractedEntityModel)
            .join(DocumentModel, ExtractedEntityModel.document_id == DocumentModel.id)
            .where(DocumentModel.session_id == session_id)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_documents_by_session(self, session_id: str) -> List[DocumentModel]:
        """
        Retrieve all document records uploaded in a session.
        """
        stmt = select(DocumentModel).where(DocumentModel.session_id == session_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
