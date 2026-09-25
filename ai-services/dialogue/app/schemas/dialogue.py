"""
Dialogue Service Data Schemas
=============================

File Purpose:
-------------
Defines the Pydantic data schemas used for dialogue requests, interview responses,
question navigation, and clinical red-flag markers.

What it does:
-------------
1. Validates incoming session interview state (previous Q&A, clinical mode: Allopathic/AYUSH).
2. Serializes outgoing question payload (question key, question text, input options, final flag).
3. Defines red-flag alert structures to notify backend of clinical emergencies.

Connected to:
-------------
- `ai-services/dialogue/app/rules/question_tree.py`: Uses these schemas to represent tree nodes.
- `ai-services/dialogue/app/services/interview_service.py`: Uses request and response models to drive conversation.
- `ai-services/dialogue/app/main.py`: Uses schemas in FastAPI route signatures.
- `backend/app/clients/dialogue_client.py`: Consumes these JSON structures from the main backend.
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class ClinicalMode(str, Enum):
    """Enumeration of clinical intake modes supported by MediKiosk."""
    ALLOPATHIC = "ALLOPATHIC"
    AYUSH = "AYUSH"


class InputType(str, Enum):
    """Input types supported on the Kiosk UI."""
    SINGLE_CHOICE = "SINGLE_CHOICE"
    MULTI_CHOICE = "MULTI_CHOICE"
    FREE_TEXT_OR_VOICE = "FREE_TEXT_OR_VOICE"
    NUMERIC = "NUMERIC"
    SCALE = "SCALE"


class PreviousAnswer(BaseModel):
    """
    Represents an already answered question in the current session.
    Used by the rules engine to branch and determine the next question.
    """
    question_key: str = Field(..., description="Unique identifier of the answered question")
    answer_text: str = Field(..., description="Patient response text or selected option key")
    input_mode: str = Field(default="TOUCH", description="TOUCH or VOICE")


class NextQuestionRequest(BaseModel):
    """
    Incoming request from Main Backend to fetch the next medical question.
    """
    session_id: str = Field(..., description="UUID of the active intake session")
    mode: ClinicalMode = Field(default=ClinicalMode.ALLOPATHIC, description="Clinical triage mode")
    language: str = Field(default="en", description="Target UI language (e.g., en, hi, mr)")
    previous_answers: List[PreviousAnswer] = Field(default_factory=list, description="List of previous Q&A turns")


class RedFlagAlert(BaseModel):
    """
    Represents an emergency clinical condition detected from patient responses.
    """
    detected: bool = Field(default=False, description="Whether an acute red flag was triggered")
    severity: str = Field(default="INFO", description="Severity level: LOW, MEDIUM, CRITICAL")
    reason: Optional[str] = Field(default=None, description="Clinical explanation for the alert")
    triage_tag: Optional[str] = Field(default=None, description="Recommended triage priority")


class NextQuestionResponse(BaseModel):
    """
    Response returned by Dialogue AI to the Main Backend with the next interview prompt.
    """
    question_key: str = Field(..., description="Unique key for this question")
    question_text: str = Field(..., description="Localized question prompt displayed/spoken to patient")
    input_type: InputType = Field(..., description="UI input method")
    options: List[str] = Field(default_factory=list, description="Selection options if applicable")
    is_final: bool = Field(default=False, description="True if interview flow is complete")
    red_flag: RedFlagAlert = Field(default_factory=RedFlagAlert, description="Red flag check result")
