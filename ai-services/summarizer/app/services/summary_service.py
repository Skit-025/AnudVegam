"""
Summarizer Service - Case Note Pipeline Coordinator
===================================================

File Purpose:
-------------
Coordinates the clinical summarization pipeline: ingests interview answers and OCR entities,
selects appropriate prompts (Allopathic or AYUSH), queries the LLM client / synthesis engine,
parses sections, and enforces safety disclaimers.

What it does:
-------------
1. Validates and extracts key facts from `SummaryGenerationRequest`.
2. Assembles structured prompt via `ClinicalPromptBuilder`.
3. Calls `LLMClient` to obtain draft clinical documentation in real time.
4. Parses raw LLM text into standardized clinical fields (Chief complaint, HPI, Meds, Labs).
5. Enforces mandatory disclaimer: "AI-drafted. Physician review required before use." and sets `reviewed = False`.
"""

import re
from typing import List
from ..schemas.summary import SummaryGenerationRequest, StructuredClinicalSummary
from ..prompts.clinical_prompts import ClinicalPromptBuilder, SYSTEM_CLINICAL_INSTRUCTION, AYUSH_CLINICAL_INSTRUCTION
from .llm_client import LLMClient


class CaseSummaryPipelineService:
    """
    Coordinator for clinical note summarization pipeline.
    """

    def __init__(self):
        self.prompt_builder = ClinicalPromptBuilder()
        self.llm_client = LLMClient()

    async def generate_summary(self, request: SummaryGenerationRequest) -> StructuredClinicalSummary:
        """
        Generate structured clinical summary draft for a given intake session in real time.
        """
        # Step 1: Select prompt construction based on clinical mode
        if request.mode.upper() == "AYUSH":
            prompt = self.prompt_builder.build_ayush_prompt(request)
            system_instruction = AYUSH_CLINICAL_INSTRUCTION
        else:
            prompt = self.prompt_builder.build_allopathic_prompt(request)
            system_instruction = SYSTEM_CLINICAL_INSTRUCTION

        # Step 2: Generate draft completion via LLM client or dynamic synthesizer
        raw_completion = await self.llm_client.generate_completion(prompt, system_instruction)

        # Step 3: Extract structured fields for UI display
        # Chief Complaint
        cc_val = "General Consultation"
        for ans in request.responses:
            if "chief_complaint" in ans.question_key:
                cc_val = ans.answer_text
                break

        # History of Presenting Illness
        hpi_val = f"Patient presents with {cc_val}."
        hpi_match = re.search(r"HISTORY OF PRESENTING ILLNESS.*?:(.*?)(?=PAST MEDICAL|CURRENT MEDICATIONS|$)", raw_completion, re.DOTALL)
        if hpi_match:
            hpi_val = hpi_match.group(1).strip()

        # Past Medical History
        pmh_val = "None reported"
        for ans in request.responses:
            if "past_medical_history" in ans.question_key:
                pmh_val = ans.answer_text
                break

        # Current Medications
        medications_list: List[str] = []
        for ent in request.extracted_entities:
            if ent.entity_type.upper() == "MEDICINE":
                medications_list.append(ent.entity_value)
        for ans in request.responses:
            if "current_medications" in ans.question_key and "taking" in ans.answer_text.lower():
                medications_list.append(ans.answer_text)

        # Allergies
        allergies_list: List[str] = []
        for ans in request.responses:
            if "allergies" in ans.question_key:
                allergies_list.append(ans.answer_text)

        # Abnormal Findings
        abnormal_list: List[str] = []
        for ent in request.extracted_entities:
            if ent.is_abnormal or ent.entity_type.upper() == "LAB_VALUE":
                abnormal_list.append(ent.entity_value)

        # Step 4: Ensure mandatory disclaimer exists in raw text
        disclaimer_text = "AI-drafted. Physician review required before use."
        if disclaimer_text not in raw_completion:
            raw_completion += f"\n\n{disclaimer_text}"

        return StructuredClinicalSummary(
            session_id=request.session_id,
            chief_complaint=cc_val,
            hpi=hpi_val,
            past_history=pmh_val,
            current_medications=list(dict.fromkeys(medications_list)),
            allergies=list(dict.fromkeys(allergies_list)),
            abnormal_findings=list(dict.fromkeys(abnormal_list)),
            ayush_observations="AYUSH clinical markers captured." if request.mode.upper() == "AYUSH" else None,
            raw_ai_draft=raw_completion,
            disclaimer=disclaimer_text,
            reviewed=False
        )
