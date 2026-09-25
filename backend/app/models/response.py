"""
History Response ORM Model (`history_responses` table)
======================================================

File Purpose:
-------------
Stores each Q&A turn collected during the interactive patient interview on the kiosk.

What it does:
-------------
1. Records question key, original question text, and patient's answer.
2. Tracks input mode (TOUCH or VOICE).
3. Flags if the response triggered a clinical red flag (e.g., chest pain, respiratory distress).
4. Maintains sequence order to preserve chronological conversation history.

Connected to:
-------------
- `backend/app/models/session.py`: Belongs to `SessionModel`.
- `backend/app/clients/dialogue_client.py`: Supplies previous turns when requesting next question.
- `backend/app/clients/summarizer_client.py`: Fed into prompt synthesis.
"""

import uuid
from typing import Optional
from sqlalchemy import String, Text, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin


class HistoryResponseModel(Base, TimestampMixin):
    """
    SQLAlchemy model representing the 'history_responses' database table.
    """
    __tablename__ = "history_responses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False)
    question_key: Mapped[str] = mapped_column(String(64), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    input_mode: Mapped[str] = mapped_column(String(16), default="TOUCH")  # TOUCH or VOICE
    is_red_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    red_flag_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    session: Mapped["SessionModel"] = relationship("SessionModel", back_populates="responses")
