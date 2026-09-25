"""
Summarizer Service - Clinical Note Prompt Engineering
=====================================================

File Purpose:
-------------
Defines clinical system instructions, prompt templates, and prompt builders
for drafting physician-ready outpatient case notes from structured intake data.

What it does:
-------------
1. Assembles patient demographics, Q&A interview turns, and OCR entities into standard clinical prompts.
2. Prevents hallucinations and enforces safety instructions.
3. Provides specialized prompt templates for Allopathic OPD and AYUSH OPD intake.
"""

from typing import Dict, Any
from ..schemas.summary import SummaryGenerationRequest


SYSTEM_CLINICAL_INSTRUCTION = """You are a senior clinical documentation specialist at an outpatient hospital reception kiosk.
Your task is to synthesize structured patient interview answers and OCR entities into a concise, professional clinical case-note draft for the attending physician.

MANDATORY RULES:
1. Do NOT diagnose or prescribe treatment.
2. Rely strictly on facts reported by the patient or extracted from documents.
3. Organize into clear sections: Chief Complaint, History of Presenting Illness (HPI), Past Medical History, Current Medications, Known Allergies, and Pertinent Lab/Document Findings.
4. Flag any red-flag emergency symptoms or abnormal lab values prominently.
5. End your output with: "AI-drafted. Physician review required before use."
"""

AYUSH_CLINICAL_INSTRUCTION = """You are an expert AYUSH clinical documentation assistant for an Indian traditional medicine OPD kiosk.
Organize collected patient intake data into standard AYUSH clinical sections:
1. Chief Complaint (Pradhana Vedana)
2. Rogi Pariksha indicators: Agni (Digestive Fire), Koshta (Bowel), Nidra (Sleep), Prakriti/Dosha physical traits.
3. Ongoing Medications (Ayurvedic and Allopathic).
4. Pertinent Findings & Flagged Symptoms.
5. End with: "AI-drafted. Physician review required before use."
"""


class ClinicalPromptBuilder:
    """
    Constructs prompt payloads for LLM invocation based on clinical mode and collected intake data.
    """

    def build_allopathic_prompt(self, request: SummaryGenerationRequest) -> str:
        """
        Build structured prompt for Allopathic clinical case summary in real time.
        """
        demographics = (
            f"Patient Name: {request.patient.name}\n"
            f"Age: {request.patient.age} years | Gender: {request.patient.gender}\n"
            f"Preferred Language: {request.patient.preferred_language}\n"
            f"Encounter ID: {request.session_id}\n"
        )

        qa_lines = []
        for ans in request.responses:
            qa_lines.append(f"- Q ({ans.question_key}): {ans.question_text}\n  A: {ans.answer_text}")
        qa_text = "\n".join(qa_lines) if qa_lines else "No interview responses recorded."

        med_lines = []
        lab_lines = []
        date_lines = []
        for ent in request.extracted_entities:
            if ent.entity_type.upper() == "MEDICINE":
                med_lines.append(f"- {ent.entity_value}")
            elif ent.entity_type.upper() == "LAB_VALUE":
                abn = " [FLAGGED ABNORMAL]" if ent.is_abnormal else ""
                lab_lines.append(f"- {ent.entity_value}{abn}")
            elif ent.entity_type.upper() == "DOCUMENT_DATE":
                date_lines.append(f"- {ent.entity_value}")

        med_text = "\n".join(med_lines) if med_lines else "None extracted from uploaded records."
        lab_text = "\n".join(lab_lines) if lab_lines else "No abnormal lab findings detected."

        prompt = f"""### PATIENT DEMOGRAPHICS
{demographics}

### PATIENT CASE-TAKING INTERVIEW (Q&A)
{qa_text}

### PREVIOUS PRESCRIPTION MEDICATIONS (VIA OCR)
{med_text}

### RECENT LABORATORY / DIAGNOSTIC FINDINGS (VIA OCR)
{lab_text}

Please generate the structured OPD clinical note draft according to the system instructions.
"""
        return prompt

    def build_ayush_prompt(self, request: SummaryGenerationRequest) -> str:
        """
        Build specialized prompt for AYUSH clinical case summary in real time.
        """
        demographics = (
            f"Patient Name: {request.patient.name}\n"
            f"Age: {request.patient.age} years | Gender: {request.patient.gender}\n"
            f"Encounter ID: {request.session_id}\n"
        )

        qa_lines = [f"- {ans.question_key}: {ans.answer_text}" for ans in request.responses]
        qa_text = "\n".join(qa_lines) if qa_lines else "No AYUSH interview responses recorded."

        med_lines = [f"- {ent.entity_value}" for ent in request.extracted_entities if ent.entity_type.upper() == "MEDICINE"]
        med_text = "\n".join(med_lines) if med_lines else "None recorded."

        prompt = f"""### AYUSH PATIENT DEMOGRAPHICS
{demographics}

### AYUSH CASE-TAKING RESPONSES (AGNI, KOSHTA, NIDRA, PRAKRITI)
{qa_text}

### CURRENT MEDICATIONS (ALLOPATHIC / AYURVEDIC)
{med_text}

Please synthesize into a clean AYUSH clinical case note draft.
"""
        return prompt
