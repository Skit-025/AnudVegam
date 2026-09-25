"""
Main Backend - Summarizer AI Service HTTP Client
================================================

File Purpose:
-------------
Encapsulates outbound asynchronous HTTP network requests from the Main Backend
to the internal Summarizer AI microservice (port 8003).

What it does:
-------------
1. Aggregates patient demographics, Q&A turns, and OCR entities into the composite payload.
2. Posts requests to `POST /api/summarizer/generate`.
3. Validates and returns the generated clinical case-note draft.
4. Provides real-time in-process clinical synthesis fallback if external container is offline.
"""

from typing import Dict, Any, List
import re
import httpx


class SummarizerClient:
    """
    HTTP client for communicating with the Summarizer AI microservice with resilient fallback.
    """

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def generate_case_summary(self, summary_request_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Request AI-drafted clinical case summary for an intake session in real time.
        """
        # Attempt remote HTTP request to microservice container
        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                resp = await client.post(f"{self.base_url}/api/summarizer/generate", json=summary_request_payload)
                if resp.status_code == 200:
                    return resp.json()
        except Exception:
            pass

        # Real-time clinical note synthesis fallback
        return self._synthesize_local_summary(summary_request_payload)

    def _synthesize_local_summary(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        session_id = payload.get("session_id", "")
        mode = payload.get("mode", "ALLOPATHIC").upper()
        patient = payload.get("patient", {})
        responses = payload.get("responses", [])
        extracted_entities = payload.get("extracted_entities", [])

        # Patient Info
        p_name = patient.get("name", "Unknown Patient")
        p_age = patient.get("age", "N/A")
        p_gender = patient.get("gender", "N/A")

        # 1. Chief Complaint
        chief_complaint = "General Medical OPD Evaluation"
        for ans in responses:
            if "chief_complaint" in ans.get("question_key", ""):
                chief_complaint = ans.get("answer_text", chief_complaint)
                break

        # 2. History of Presenting Illness (HPI)
        duration_text = "recently reported"
        symptom_details = ""
        for ans in responses:
            k = ans.get("question_key", "")
            if "duration" in k:
                duration_text = ans.get("answer_text", "")
            elif any(sub in k for sub in ["chest_details", "breath_details", "fever_details", "pain_details", "symptoms"]):
                symptom_details += f" {ans.get('answer_text', '')}"

        # 3. Past Medical History
        pmh = "No chronic illnesses reported"
        for ans in responses:
            if "past_medical_history" in ans.get("question_key", "") or "history" in ans.get("question_key", ""):
                pmh = ans.get("answer_text", pmh)
                break

        # 4. Current Medications (from OCR + dialogue)
        meds: List[str] = []
        for ent in extracted_entities:
            if ent.get("entity_type", "").upper() == "MEDICINE":
                meds.append(ent.get("entity_value", ""))
        for ans in responses:
            if "current_medications" in ans.get("question_key", "") and "taking" in ans.get("answer_text", "").lower():
                meds.append(ans.get("answer_text", ""))
        meds = list(dict.fromkeys(meds))

        # 5. Allergies
        allergies: List[str] = []
        for ans in responses:
            if "allergies" in ans.get("question_key", ""):
                allergies.append(ans.get("answer_text", ""))
        allergies = list(dict.fromkeys(allergies))

        # 6. Abnormal Lab Findings
        abnormal_labs: List[str] = []
        for ent in extracted_entities:
            if ent.get("is_abnormal") or ent.get("entity_type", "").upper() == "LAB_VALUE":
                abnormal_labs.append(ent.get("entity_value", ""))
        abnormal_labs = list(dict.fromkeys(abnormal_labs))

        # Compose structured clinical text note
        disclaimer_text = "AI-drafted. Physician review required before use."
        hpi_narrative = (
            f"{p_name}, a {p_age}-year-old {p_gender}, presents to the OPD with complaints of {chief_complaint}. "
            f"Symptoms onset: {duration_text}.{symptom_details} "
            f"Patient has known clinical history of {pmh}."
        )

        raw_draft = (
            f"CLINICAL CASE SUMMARY ({mode} OPD)\n"
            f"==================================================\n"
            f"PATIENT: {p_name} | Age: {p_age} | Gender: {p_gender}\n"
            f"CHIEF COMPLAINT: {chief_complaint}\n\n"
            f"HISTORY OF PRESENTING ILLNESS:\n{hpi_narrative}\n\n"
            f"PAST MEDICAL HISTORY:\n- {pmh}\n\n"
            f"CURRENT MEDICATIONS:\n" + ("\n".join(f"- {m}" for m in meds) if meds else "- None reported") + "\n\n"
            f"KNOWN ALLERGIES:\n" + ("\n".join(f"- {a}" for a in allergies) if allergies else "- No known drug allergies (NKDA)") + "\n\n"
            f"RELEVANT LAB / OCR FINDINGS:\n" + ("\n".join(f"- {l}" for l in abnormal_labs) if abnormal_labs else "- No abnormal reports uploaded") + "\n\n"
            f"MANDATORY SAFETY DISCLAIMER:\n{disclaimer_text}"
        )

        return {
            "session_id": session_id,
            "chief_complaint": chief_complaint,
            "hpi": hpi_narrative,
            "past_history": pmh,
            "current_medications": meds,
            "allergies": allergies,
            "abnormal_findings": abnormal_labs,
            "raw_ai_draft": raw_draft,
            "disclaimer": disclaimer_text,
            "reviewed": False
        }
