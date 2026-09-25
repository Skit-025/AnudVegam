"""
Main Backend - Dialogue AI Service HTTP Client
==============================================

File Purpose:
-------------
Encapsulates asynchronous HTTP network requests from the Main Backend
to the internal Dialogue AI microservice (port 8001).

What it does:
-------------
1. Posts requests to `POST /api/dialogue/next-question`.
2. Connects to the standalone microservice container via HTTP.
3. Automatically evaluates dynamic clinical branching and red flags if external service is offline.
"""

from typing import Dict, Any, List
import re
import httpx


class DialogueClient:
    """
    HTTP client for communicating with the Dialogue AI microservice with resilient fallback.
    """

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def fetch_next_question(
        self,
        session_id: str,
        mode: str,
        language: str,
        previous_answers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Query Dialogue AI service for the next clinical interview question and red-flag check in real time.
        """
        payload = {
            "session_id": session_id,
            "mode": mode.upper(),
            "language": language,
            "previous_answers": previous_answers
        }

        # Attempt remote HTTP request to microservice
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.post(f"{self.base_url}/api/dialogue/next-question", json=payload)
                if resp.status_code == 200:
                    return resp.json()
        except Exception:
            pass

        # Real-time in-process question navigation & red-flag detection fallback
        return self._compute_local_step(session_id, mode, language, previous_answers)

    def _compute_local_step(
        self,
        session_id: str,
        mode: str,
        language: str,
        previous_answers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        # 1. Evaluate Red Flags
        red_flag = {"detected": False, "severity": "INFO", "reason": None}
        combined_text = " ".join([str(a.get("answer_text", "")).lower() for a in previous_answers])

        if any(w in combined_text for w in ["chest pain", "crushing", "radiating", "heart attack", "chhati", "dharakan"]):
            if any(w in combined_text for w in ["arm", "shoulder", "sweat", "jaw", "breathless", "left"]):
                red_flag = {
                    "detected": True,
                    "severity": "CRITICAL",
                    "reason": "Potential Acute Coronary Syndrome / Myocardial Infarction symptom detected."
                }
            else:
                red_flag = {
                    "detected": True,
                    "severity": "URGENT",
                    "reason": "Cardiopulmonary distress warning: Chest discomfort."
                }
        elif any(w in combined_text for w in ["unconscious", "fainted", "blood in cough", "hemoptysis", "stroke", "paralysis"]):
            red_flag = {
                "detected": True,
                "severity": "CRITICAL",
                "reason": "Acute medical emergency marker flagged for immediate clinical attention."
            }

        answered_keys = [a.get("question_key") for a in previous_answers]

        # 2. Dynamic Question Branching
        if "chief_complaint" not in answered_keys:
            if language == "hi":
                q_text = "आज आप अस्पताल किस स्वास्थ्य समस्या के कारण आए हैं?"
                opts = ["सीने में दर्द / दबाव", "तेज बुखार और खांसी", "पेट में दर्द / उल्टी", "चक्कर / घबराहट", "अन्य"]
            elif language == "or":
                q_text = "ଆଜି ଆପଣ କେଉଁ ସ୍ୱାସ୍ଥ୍ୟ ସମସ୍ୟା ପାଇଁ ଡାକ୍ତରଖାନା ଆସିଛନ୍ତି?"
                opts = ["ଛାତି ଯନ୍ତ୍ରଣା", "ଜ୍ୱର ଏବଂ କାଶ", "ପେଟ ଯନ୍ତ୍ରଣା", "ଅନ୍ୟାନ୍ୟ"]
            else:
                q_text = "What is your main health concern or reason for visiting the OPD today?"
                opts = ["Chest Discomfort / Pain", "High Fever & Cough", "Abdominal Pain", "Dizziness / Fatigue", "Joint Pain", "Routine Checkup"]

            return {
                "question_key": "chief_complaint",
                "question_text": q_text,
                "input_type": "FREE_TEXT_OR_VOICE",
                "options": opts,
                "is_final": False,
                "red_flag": red_flag
            }

        # Branch based on Chief Complaint
        cc_text = ""
        for a in previous_answers:
            if a.get("question_key") == "chief_complaint":
                cc_text = str(a.get("answer_text", "")).lower()

        if ("chest" in cc_text or "heart" in cc_text or "chhati" in cc_text) and "chest_details" not in answered_keys:
            return {
                "question_key": "chest_details",
                "question_text": "Describe the chest discomfort: Is it crushing heaviness, sharp pricking, burning, or aching?",
                "input_type": "CHIP_SELECTION",
                "options": ["Heavy Crushing Pressure", "Sharp Pricking Pain", "Burning / Acidity sensation", "Dull Constant Ache"],
                "is_final": False,
                "red_flag": red_flag
            }

        if ("fever" in cc_text or "temp" in cc_text or "bukhar" in cc_text) and "fever_details" not in answered_keys:
            return {
                "question_key": "fever_details",
                "question_text": "What is your highest recorded temperature and do you have chills or body ache?",
                "input_type": "FREE_TEXT_OR_VOICE",
                "options": ["High fever with chills (>102 F)", "Moderate fever (100-101 F)", "Mild low-grade fever"],
                "is_final": False,
                "red_flag": red_flag
            }

        if "duration" not in answered_keys:
            return {
                "question_key": "duration",
                "question_text": "How many days or hours have you been experiencing this discomfort?",
                "input_type": "CHIP_SELECTION",
                "options": ["Less than 6 hours (Acute)", "1 to 3 days", "1 to 2 weeks", "More than a month (Chronic)"],
                "is_final": False,
                "red_flag": red_flag
            }

        if "past_medical_history" not in answered_keys:
            return {
                "question_key": "past_medical_history",
                "question_text": "Do you have any existing health conditions like Diabetes, Blood Pressure, Thyroid, or Heart disease?",
                "input_type": "MULTI_SELECT",
                "options": ["Diabetes (High Sugar)", "Hypertension (High BP)", "Thyroid Disorder", "Heart Disease", "None / Healthy"],
                "is_final": False,
                "red_flag": red_flag
            }

        if "current_medications" not in answered_keys:
            return {
                "question_key": "current_medications",
                "question_text": "Are you currently taking any daily prescribed medicines or Ayurvedic preparations?",
                "input_type": "FREE_TEXT_OR_VOICE",
                "options": ["Taking regular daily medicines", "Not taking any medicines currently", "Only taking Ayurvedic / Homeopathy"],
                "is_final": False,
                "red_flag": red_flag
            }

        if "allergies" not in answered_keys:
            return {
                "question_key": "allergies",
                "question_text": "Do you have any known allergies to medicines (like Penicillin, Sulfa), foods, or dust?",
                "input_type": "CHIP_SELECTION",
                "options": ["No known drug allergies (NKDA)", "Allergic to specific antibiotics", "Skin / Food allergies"],
                "is_final": False,
                "red_flag": red_flag
            }

        # Intake complete
        return {
            "question_key": "intake_completed",
            "question_text": "Thank you. Your preliminary clinical intake is complete. Please review the summary.",
            "input_type": "TOUCH_CONFIRM",
            "options": ["Review Case Summary"],
            "is_final": True,
            "red_flag": red_flag
        }
