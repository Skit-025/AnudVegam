"""
Dialogue Service - Clinical Red-Flag Rule Engine
=================================================

File Purpose:
-------------
Real-time evaluation of patient symptoms, duration, and questionnaire responses
against clinical safety triggers and emergency indicators.

What it does:
-------------
1. Scans patient's current and past responses for critical danger signs (e.g. cardiac distress,
   stroke symptoms, acute breathlessness, high fever with altered sensorium, uncontrolled bleeding).
2. Generates an immediate triage alert flag with severity (CRITICAL, URGENT, MONITOR).
3. Analyzes both individual responses and cumulative multi-symptom risks in real-time.

Connected to:
-------------
- `ai-services/dialogue/app/schemas/dialogue.py`: Uses `RedFlagAlert` schema for structured output.
- `ai-services/dialogue/app/services/interview_service.py`: Evaluates every interview turn.
- Main Backend: Passed through to `backend/app/models/response.py` to flag the doctor's queue.
"""

import re
from typing import List, Dict, Any, Tuple
from ..schemas.dialogue import PreviousAnswer, RedFlagAlert


class RedFlagRuleEngine:
    """
    Evaluates patient responses against emergency clinical trigger rules in real time.
    Does NOT make an autonomous diagnosis or replace physician assessment.
    """

    def __init__(self):
        # Critical emergency patterns (Immediate OPD triage / ER escalation)
        self.critical_patterns: List[Tuple[re.Pattern, str, str]] = [
            (
                re.compile(r"\b(chest\s+pain|chest\s+pressure|chest\s+tightness|heaviness\s+in\s+chest|crushing\s+pain)\b", re.IGNORECASE),
                "CRITICAL",
                "Potential Acute Coronary Syndrome / Myocardial Infarction symptom detected."
            ),
            (
                re.compile(r"\b(radiat(ing|es)?\s+to\s+(left\s+arm|jaw|neck|shoulder|back))\b", re.IGNORECASE),
                "CRITICAL",
                "Radiation of pain to arm/jaw is a high-risk cardiac warning sign."
            ),
            (
                re.compile(r"\b(shortness\s+of\s+breath|difficulty\s+breathing|breathless(ness)?|gasping|cannot\s+breathe|choking)\b", re.IGNORECASE),
                "CRITICAL",
                "Severe respiratory distress or acute pulmonary compromise detected."
            ),
            (
                re.compile(r"\b(unconscious|passed\s+out|fainted|loss\s+of\s+consciousness|seizure|convulsion|blackout)\b", re.IGNORECASE),
                "CRITICAL",
                "Loss of consciousness or neurological deficit requires immediate assessment."
            ),
            (
                re.compile(r"\b(coughing\s+blood|hemoptysis|vomiting\s+blood|hematemesis|blood\s+in\s+stool|melena|black\s+tarry)\b", re.IGNORECASE),
                "CRITICAL",
                "Active internal or gastrointestinal / pulmonary hemorrhage detected."
            ),
            (
                re.compile(r"\b(sudden\s+weakness|facial\s+droop|slurred\s+speech|cannot\s+speak|arm\s+numbness|one\s+side\s+paralysis)\b", re.IGNORECASE),
                "CRITICAL",
                "FAST signs: Acute Cerebrovascular Accident (Stroke) alert."
            ),
            (
                re.compile(r"\b(suicid(al|e)|kill\s+myself|end\s+my\s+life|harm\s+myself)\b", re.IGNORECASE),
                "CRITICAL",
                "Immediate psychiatric emergency / self-harm risk detected."
            )
        ]

        # Urgent patterns (Prompt doctor review needed)
        self.urgent_patterns: List[Tuple[re.Pattern, str, str]] = [
            (
                re.compile(r"\b(high\s+fever|fever\s+(above|over|>)\s*(102|103|104|39|40))\b", re.IGNORECASE),
                "URGENT",
                "High-grade fever detected; assess for systemic infection/sepsis."
            ),
            (
                re.compile(r"\b(severe\s+headache|worst\s+headache\s+of\s+life|thunderclap)\b", re.IGNORECASE),
                "URGENT",
                "Thunderclap or acute severe headache requires urgent neurological exclusion."
            ),
            (
                re.compile(r"\b(severe\s+abdominal\s+pain|acute\s+abdomen|rigid\s+belly)\b", re.IGNORECASE),
                "URGENT",
                "Severe acute abdomen requires clinical exclusion of appendicitis/perforation."
            ),
            (
                re.compile(r"\b(stiff\s+neck|neck\s+rigidity\s+with\s+fever|photophobia)\b", re.IGNORECASE),
                "URGENT",
                "Meningeal signs: Fever with stiff neck requires immediate triage."
            ),
            (
                re.compile(r"\b(anaphylaxis|swollen\s+lips|swollen\s+tongue|throat\s+closing|hives\s+all\s+over)\b", re.IGNORECASE),
                "CRITICAL",
                "Potential severe allergic reaction / anaphylactic airway compromise."
            )
        ]

    def evaluate_response(self, question_key: str, answer_text: str) -> RedFlagAlert:
        """
        Evaluate a single response against critical emergency rules in real time.
        """
        if not answer_text or not answer_text.strip():
            return RedFlagAlert(detected=False, severity="INFO", reason=None)

        text = answer_text.strip().lower()

        # Check critical emergency patterns first
        for pattern, severity, reason in self.critical_patterns:
            if pattern.search(text):
                return RedFlagAlert(
                    detected=True,
                    severity=severity,
                    reason=reason,
                    triage_tag="PRIORITY_RED"
                )

        # Check urgent warning patterns
        for pattern, severity, reason in self.urgent_patterns:
            if pattern.search(text):
                return RedFlagAlert(
                    detected=True,
                    severity=severity,
                    reason=reason,
                    triage_tag="PRIORITY_YELLOW"
                )

        return RedFlagAlert(detected=False, severity="INFO", reason=None, triage_tag="STANDARD_GREEN")

    def evaluate_cumulative_history(self, history: List[PreviousAnswer]) -> RedFlagAlert:
        """
        Evaluate composite patient answers across the entire session for combined risks
        (e.g., patient reporting fever + stiff neck, or diabetic patient with chest tightness).
        """
        if not history:
            return RedFlagAlert(detected=False, severity="INFO", reason=None)

        combined_text = " ".join([f"{item.question_key}: {item.answer_text}" for item in history]).lower()

        # Composite Risk 1: Fever + Altered sensorium / confusion / stiff neck
        has_fever = bool(re.search(r"\b(fever|chills|temperature|bukhar)\b", combined_text))
        has_neuro = bool(re.search(r"\b(stiff\s+neck|confusion|disoriented|drowsy|delirium)\b", combined_text))
        if has_fever and has_neuro:
            return RedFlagAlert(
                detected=True,
                severity="CRITICAL",
                reason="Composite Risk: Fever combined with altered sensorium or meningeal signs.",
                triage_tag="PRIORITY_RED"
            )

        # Composite Risk 2: Diabetes / Hypertension history + Chest symptoms
        has_cv_risk = bool(re.search(r"\b(diabet(es|ic)|hypertens(ion|ive)|bp\s+high|sugar)\b", combined_text))
        has_chest = bool(re.search(r"\b(chest\s+discomfort|breathless|sweating|palpitation)\b", combined_text))
        if has_cv_risk and has_chest:
            return RedFlagAlert(
                detected=True,
                severity="URGENT",
                reason="Composite Risk: Diabetic/Hypertensive patient presenting with cardiopulmonary symptoms.",
                triage_tag="PRIORITY_YELLOW"
            )

        # Check individual critical matches across all answers
        for item in history:
            alert = self.evaluate_response(item.question_key, item.answer_text)
            if alert.detected and alert.severity == "CRITICAL":
                return alert

        return RedFlagAlert(detected=False, severity="INFO", reason=None, triage_tag="STANDARD_GREEN")
