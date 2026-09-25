"""
OCR Service - Clinical Entity Extraction Engine
================================================

File Purpose:
-------------
Parses raw OCR text from prescriptions, lab reports, and clinical records
to extract structured medical concepts:
- Active medications, formulations, dosages, and dosing frequencies
- Laboratory tests, quantitative numerical values, units, and abnormality indicators
- Document and consultation dates
- Provisional or historical clinical diagnoses

What it does:
-------------
1. Executes multi-pass regular expression matching and contextual window analysis.
2. Cross-references against curated lists of Indian essential drugs and formulations.
3. Automatically evaluates numerical lab findings against clinical reference ranges.
"""

import re
from typing import List, Dict, Any, Optional
from ..schemas.ocr import ExtractedEntity, EntityType


class ClinicalEntityExtractor:
    """
    High-accuracy regex and dictionary-based medical information extraction engine.
    """

    def __init__(self):
        # Curated dictionary of common Indian medicines and formulations
        self.medicine_dictionary = [
            # Analgesics / Antipyretics
            "paracetamol", "pcm", "crocin", "dolo", "calpol", "ibuprofen", "combiflam", "diclofenac", "voveran", "aceclofenac", "zerodol", "tramadol",
            # Gastrointestinal
            "pantoprazole", "pan", "pantocid", "omeprazole", "omez", "rabeprazole", "razo", "ranitidine", "rantac", "domperidone", "ondansetron", "emset", "antacid", "sucralfate",
            # Antibiotics & Antimicrobials
            "amoxicillin", "mox", "augmentin", "amoxyclav", "azithromycin", "azithral", "ciprofloxacin", "ciplox", "ofloxacin", "cefixime", "zifi", "doxycycline", "metronidazole", "flagyl", "norfloxacin",
            # Cardiovascular & Antihypertensives
            "amlodipine", "amlong", "stamlo", "telmisartan", "telma", "losartan", "losar", "atenolol", "betacap", "metoprolol", "envas", "enalapril", "ramipril",
            # Antidiabetics
            "metformin", "glycomet", "glimepiride", "amaryl", "gliclazide", "vildagliptin", "galvus", "sitagliptin", "januvia", "dapagliflozin", "forxiga", "insulin",
            # Respiratory & Antiallergic
            "cetirizine", "citrizine", "okacet", "levocetirizine", "levocet", "montelukast", "montair", "salbutamol", "asthalin", "budesonide", "budecort", "cough syrup",
            # Statins & Lipid Lowering
            "atorvastatin", "atorva", "rosuvastatin", "rosuvas",
            # Vitamins & Supplements
            "vitamin d3", "calcium", "shelcal", "neurobion", "becosules", "folic acid", "iron", "ferrous ascorbate", "zinc"
        ]

        # Standard lab test reference intervals
        self.lab_reference_ranges = {
            "fasting_blood_sugar": {"min": 70.0, "max": 100.0, "unit": "mg/dL", "name": "Fasting Blood Sugar (FBS)"},
            "postprandial_blood_sugar": {"min": 70.0, "max": 140.0, "unit": "mg/dL", "name": "Postprandial Blood Sugar (PPBS)"},
            "random_blood_sugar": {"min": 70.0, "max": 140.0, "unit": "mg/dL", "name": "Random Blood Sugar (RBS)"},
            "hba1c": {"min": 4.0, "max": 5.6, "unit": "%", "name": "HbA1c (Glycated Hemoglobin)"},
            "hemoglobin": {"min": 12.0, "max": 17.0, "unit": "g/dL", "name": "Hemoglobin (Hb)"},
            "wbc_count": {"min": 4000.0, "max": 11000.0, "unit": "/mcL", "name": "Total Leukocyte Count (WBC)"},
            "platelet_count": {"min": 150000.0, "max": 450000.0, "unit": "/mcL", "name": "Platelet Count"},
            "serum_creatinine": {"min": 0.6, "max": 1.2, "unit": "mg/dL", "name": "Serum Creatinine"},
            "total_bilirubin": {"min": 0.2, "max": 1.2, "unit": "mg/dL", "name": "Total Bilirubin"},
            "serum_uric_acid": {"min": 3.5, "max": 7.2, "unit": "mg/dL", "name": "Serum Uric Acid"}
        }

    def extract_dates(self, text: str) -> List[ExtractedEntity]:
        """
        Extract document or consultation dates in real time.
        """
        entities: List[ExtractedEntity] = []
        # Match DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD
        date_pattern = re.compile(r"\b(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4}|\d{4}[-/\.]\d{1,2}[-/\.]\d{1,2})\b")
        for match in date_pattern.finditer(text):
            val = match.group(1)
            entities.append(ExtractedEntity(
                entity_type=EntityType.DOCUMENT_DATE,
                entity_value=val,
                confidence=0.95
            ))
        return entities

    def extract_medications(self, text: str) -> List[ExtractedEntity]:
        """
        Scan text for pharmaceutical names, strength (mg/ml), and dosage frequency (e.g. 1-0-1, OD, BD).
        """
        entities: List[ExtractedEntity] = []
        lines = text.split("\n")

        # Regex for strength (e.g. 500mg, 10 ml, 2.5 mg)
        strength_regex = re.compile(r"\b(\d+(?:\.\d+)?\s*(?:mg|mcg|gm|ml|g))\b", re.IGNORECASE)
        # Regex for frequency (e.g. 1-0-1, 1-0-0, OD, BD, TDS, QID, HS, SOS)
        freq_regex = re.compile(r"\b(1-0-1|1-0-0|0-1-0|0-0-1|1-1-1|O\.?D\.?|B\.?D\.?|T\.?D\.?S\.?|Q\.?I\.?D\.?|H\.?S\.?|S\.?O\.?S\.?|once\s+daily|twice\s+daily)\b", re.IGNORECASE)

        seen_meds = set()

        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue

            for med in self.medicine_dictionary:
                # Word boundary search
                pattern = re.compile(r"\b" + re.escape(med) + r"\b", re.IGNORECASE)
                match = pattern.search(line_clean)
                if match and med not in seen_meds:
                    seen_meds.add(med)
                    # Look for strength and frequency on the same line
                    strength_match = strength_regex.search(line_clean)
                    freq_match = freq_regex.search(line_clean)

                    strength_str = strength_match.group(1) if strength_match else ""
                    freq_str = freq_match.group(1).upper() if freq_match else ""

                    display_val = f"Tab {med.capitalize()}"
                    if strength_str:
                        display_val += f" {strength_str}"
                    if freq_str:
                        display_val += f" ({freq_str})"

                    entities.append(ExtractedEntity(
                        entity_type=EntityType.MEDICINE,
                        entity_value=display_val,
                        confidence=0.90
                    ))

        return entities

    def extract_lab_values(self, text: str) -> List[ExtractedEntity]:
        """
        Parse laboratory tests, quantitative values, and compare against reference ranges.
        """
        entities: List[ExtractedEntity] = []

        patterns = [
            ("fasting_blood_sugar", re.compile(r"\b(?:fbs|fasting\s+(?:blood\s+)?sugar|fasting\s+glucose)[\s:]*([0-9]+(?:\.[0-9]+)?)\b", re.IGNORECASE)),
            ("postprandial_blood_sugar", re.compile(r"\b(?:ppbs|post\s*prandial[\s\w]*|pp\s+glucose)[\s:]*([0-9]+(?:\.[0-9]+)?)\b", re.IGNORECASE)),
            ("random_blood_sugar", re.compile(r"\b(?:rbs|random\s+(?:blood\s+)?sugar)[\s:]*([0-9]+(?:\.[0-9]+)?)\b", re.IGNORECASE)),
            ("hba1c", re.compile(r"\b(?:hba1c|glycated\s+h(?:a)?emoglobin)[\s:]*([0-9]+(?:\.[0-9]+)?)\s*%?", re.IGNORECASE)),
            ("hemoglobin", re.compile(r"\b(?:hb|hgb|h(?:a)?emoglobin)[\s:]*([0-9]+(?:\.[0-9]+)?)\s*(?:g/dl|gm/dl)?\b", re.IGNORECASE)),
            ("wbc_count", re.compile(r"\b(?:wbc|tlc|total\s+leukocyte\s+count)[\s:]*([0-9]+(?:,[0-9]+)?(?:\.[0-9]+)?)\b", re.IGNORECASE)),
            ("platelet_count", re.compile(r"\b(?:platelet(?:s)?(?:\s+count)?)[\s:]*([0-9]+(?:,[0-9]+)?(?:\.[0-9]+)?)\b", re.IGNORECASE)),
            ("serum_creatinine", re.compile(r"\b(?:creatinine|serum\s+creatinine)[\s:]*([0-9]+(?:\.[0-9]+)?)\b", re.IGNORECASE)),
            ("total_bilirubin", re.compile(r"\b(?:bilirubin|total\s+bilirubin)[\s:]*([0-9]+(?:\.[0-9]+)?)\b", re.IGNORECASE)),
            ("serum_uric_acid", re.compile(r"\b(?:uric\s+acid|serum\s+uric\s+acid)[\s:]*([0-9]+(?:\.[0-9]+)?)\b", re.IGNORECASE))
        ]

        for test_key, pattern in patterns:
            match = pattern.search(text)
            if match:
                val_str = match.group(1).replace(",", "")
                try:
                    num_val = float(val_str)
                    ref = self.lab_reference_ranges[test_key]
                    is_abnormal = (num_val < ref["min"]) or (num_val > ref["max"])
                    ref_str = f"{ref['min']} - {ref['max']} {ref['unit']}"

                    abnormal_tag = " [ABNORMAL HIGH]" if num_val > ref["max"] else (" [ABNORMAL LOW]" if num_val < ref["min"] else "")
                    display_text = f"{ref['name']}: {num_val} {ref['unit']}{abnormal_tag}"

                    entities.append(ExtractedEntity(
                        entity_type=EntityType.LAB_VALUE,
                        entity_value=display_text,
                        confidence=0.92,
                        is_abnormal=is_abnormal,
                        reference_range=ref_str
                    ))
                except ValueError:
                    continue

        # Blood pressure regex (e.g. 130/85 mmHg, BP: 140/90)
        bp_match = re.search(r"\b(?:bp|blood\s+pressure)[\s:]*([0-9]{2,3})\s*/\s*([0-9]{2,3})\s*(?:mmhg)?\b", text, re.IGNORECASE)
        if bp_match:
            systolic = int(bp_match.group(1))
            diastolic = int(bp_match.group(2))
            is_high = systolic >= 140 or diastolic >= 90
            bp_tag = " [ELEVATED / HYPERTENSIVE]" if is_high else " [NORMAL]"
            entities.append(ExtractedEntity(
                entity_type=EntityType.LAB_VALUE,
                entity_value=f"Blood Pressure: {systolic}/{diastolic} mmHg{bp_tag}",
                confidence=0.95,
                is_abnormal=is_high,
                reference_range="< 120/80 mmHg"
            ))

        return entities

    def extract_diagnoses(self, text: str) -> List[ExtractedEntity]:
        """
        Detect diagnostic indications and clinical impressions in text.
        """
        entities: List[ExtractedEntity] = []
        diagnoses_keywords = [
            "Type 2 Diabetes Mellitus", "Essential Hypertension", "Acute Bronchitis",
            "Bronchial Asthma", "Acute Gastroenteritis", "Dengue Fever", "Malaria",
            "Urinary Tract Infection", "Hypothyroidism", "Migraine", "Gastritis", "Allergic Rhinitis"
        ]
        for diag in diagnoses_keywords:
            if re.search(r"\b" + re.escape(diag) + r"\b", text, re.IGNORECASE):
                entities.append(ExtractedEntity(
                    entity_type=EntityType.DIAGNOSIS,
                    entity_value=diag,
                    confidence=0.88
                ))
        return entities

    def extract_all_entities(self, raw_text: str) -> List[ExtractedEntity]:
        """
        Execute comprehensive extraction pipeline over raw document text in real time.
        """
        if not raw_text:
            return []

        all_entities: List[ExtractedEntity] = []
        all_entities.extend(self.extract_dates(raw_text))
        all_entities.extend(self.extract_medications(raw_text))
        all_entities.extend(self.extract_lab_values(raw_text))
        all_entities.extend(self.extract_diagnoses(raw_text))

        # Deduplicate entities by (entity_type, entity_value)
        unique_entities: List[ExtractedEntity] = []
        seen = set()
        for ent in all_entities:
            key = (ent.entity_type, ent.entity_value.lower())
            if key not in seen:
                seen.add(key)
                unique_entities.append(ent)

        return unique_entities
