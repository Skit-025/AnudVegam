# MediKiosk System Architecture

## 1. High-Level Concept
MediKiosk is designed to operate on a touchscreen hardware terminal in a hospital OPD reception area. It replaces chaotic handwritten intake queues with a streamlined digital pipeline:
1. Patient enters ABHA/Aadhaar number or basic details.
2. Patient grants informed consent in their preferred language.
3. Patient engages in interactive symptom interview (Allopathic or AYUSH).
4. Patient places past prescriptions/lab reports under a kiosk scanner.
5. AI aggregates patient responses + OCR entities into a draft case summary.
6. Doctor reviews, edits, and confirms the note on their OPD dashboard.
7. System generates a standardized ABDM-compliant FHIR JSON export.

## 2. Component Diagram & Interconnectivity
```
+-----------------------------------------------------------+
|               Kiosk Frontend (React + Vite)               |
|  [Identify] -> [Converse] -> [Scan] -> [Summary/Consult]  |
+-----------------------------+-----------------------------+
                              | REST JSON (HTTP)
                              v
+-----------------------------------------------------------+
|          Main Backend Orchestrator (FastAPI:8000)         |
|  - Auth & Patient Management    - Database ORM Layer      |
|  - Session Lifecycle Engine     - Doctor Review Controller|
+-----------+-----------------+------------------+----------+
            |                 |                  |
            | HTTP /next-q    | HTTP /extract    | HTTP /summarize
            v                 v                  v
    +---------------+ +---------------+ +-------------------+
    |Dialogue AI    | |OCR AI         | |Summarizer AI      |
    |(:8001)        | |(:8002)        | |(:8003)            |
    |- Question tree|- Preprocessing  |- Clinical prompts   |
    |- Red-flag rule|- Tesseract OCR  |- LLM integration    |
    |               |- Entity regex   |                     |
    +---------------+ +---------------+ +-------------------+
            |                 |                  |
            +-----------------+------------------+
                              |
                              v
                   +---------------------+
                   | PostgreSQL Database |
                   | (9 Relational Tables|
                   +---------------------+
```

## 3. Human-in-the-Loop & Safety Principles
- **No Autonomous Diagnosis**: The AI never generates prescriptions or medical diagnoses directly for the patient.
- **Draft Status Mandatory**: All AI summaries must carry the warning `"AI-drafted. Physician review required before use."` programmatically.
- **Explicit Physician Verification**: The summary is not locked or exportable to FHIR until `reviewed = true` is signed by the attending doctor.
- **Red-Flag Escalation**: Severe warning indicators (e.g., severe chest pain, sudden breathlessness, acute fever) trigger real-time triage flags on the doctor's consult queue.
