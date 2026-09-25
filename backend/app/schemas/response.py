"""
History Response Pydantic Schemas
=================================

File Purpose:
-------------
Defines request and response schemas for patient Q&A answers, input mode tracking,
and red-flag alert propagation.

Connected to:
-------------
- `backend/app/api/sessions.py`: Handlers for `/api/sessions/{id}/responses`.
- `backend/app/models/response.py`: Maps to `HistoryResponseModel`.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class AnswerSubmissionRequest(BaseModel):
    """Payload when patient answers a question at the kiosk."""
    question_key: str = Field(..., description="Unique key of the question being answered")
    question_text: str = Field(..., description="Prompt that was presented to the patient")
    answer_text: str = Field(..., description="Patient response (text or selected option)")
    input_mode: str = Field(default="TOUCH", description="TOUCH or VOICE")


class HistoryResponseItem(BaseModel):
    """Recorded Q&A response item."""
    id: str
    sequence_order: int
    question_key: str
    question_text: str
    answer_text: str
    input_mode: str
    is_red_flag: bool
    red_flag_reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
