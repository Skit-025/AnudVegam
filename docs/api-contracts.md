# MediKiosk API Contracts

## 1. Main Backend API Endpoints (Port 8000)

### `POST /api/patients`
- **Purpose**: Register or identify patient using ABHA ID, Aadhaar number, or demographic details.
- **Request Body**:
  ```json
  {
    "abha_id": "14-digit-mock-abha",
    "name": "Ramesh Kumar",
    "age": 45,
    "gender": "MALE",
    "phone": "9876543210",
    "preferred_language": "hi"
  }
  ```
- **Response**: `201 Created` with patient ID and demographic details.

---

### `POST /api/consents`
- **Purpose**: Record patient consent for digital intake and AI-assisted clinical summary generation.
- **Request Body**:
  ```json
  {
    "patient_id": "uuid",
    "consent_granted": true,
    "consent_text": "I authorize collection of symptom and medical history for OPD triage.",
    "language": "hi"
  }
  ```
- **Response**: `200 OK` with consent timestamp and token.

---

### `POST /api/sessions`
- **Purpose**: Start an active case-taking session.
- **Request Body**:
  ```json
  {
    "patient_id": "uuid",
    "mode": "ALLOPATHIC" // or "AYUSH"
  }
  ```
- **Response**: `201 Created` with `session_id`, `status: "ACTIVE"`.

---

### `POST /api/sessions/{id}/responses`
- **Purpose**: Submit patient's answer to the current question, evaluate red-flags, and advance session.
- **Request Body**:
  ```json
  {
    "question_key": "chief_complaint",
    "answer_text": "Severe chest pain radiating to left arm for 2 hours",
    "input_mode": "TOUCH" // or "VOICE"
  }
  ```
- **Response**: `200 OK` with response ID and red flag status.

---

### `GET /api/sessions/{id}/next-question`
- **Purpose**: Retrieve the next medical interview question from the Dialogue AI service.
- **Response**:
  ```json
  {
    "question_key": "symptom_duration",
    "question_text": "How many days have you had this symptom?",
    "input_type": "CHOICE",
    "options": ["< 1 day", "1-3 days", "> 1 week"],
    "is_final": false,
    "red_flag_alert": false
  }
  ```

---

### `POST /api/sessions/{id}/documents`
- **Purpose**: Upload scanned prescription or diagnostic test image for OCR processing.
- **Request**: Multipart `file` (image/png, image/jpeg, application/pdf).
- **Response**: `201 Created` with extracted entities (medicines, lab values, dates, diagnoses).

---

### `POST /api/sessions/{id}/summary`
- **Purpose**: Trigger LLM summarizer pipeline to compile draft case summary from responses and OCR.
- **Response**:
  ```json
  {
    "summary_id": "uuid",
    "chief_complaint": "Chest pain radiating to arm",
    "hpi": "History of presenting illness text...",
    "past_history": "Hypertension for 5 years",
    "current_medications": ["Amlodipine 5mg"],
    "red_flags": ["Potential Acute Coronary Syndrome"],
    "disclaimer": "AI-drafted. Physician review required before use.",
    "reviewed": false
  }
  ```

---

### `PUT /api/sessions/{id}/summary`
- **Purpose**: Doctor edits and signs off on the case summary.
- **Request Body**:
  ```json
  {
    "physician_id": "dr_sharma_01",
    "edited_summary": "Doctor verified notes...",
    "clinical_assessment": "Stable angina, rule out NSTEMI",
    "reviewed": true
  }
  ```
- **Response**: `200 OK` with updated status.

---

### `POST /api/sessions/{id}/fhir-export`
- **Purpose**: Generate ABDM-compliant FHIR Bundle JSON for digital health records.
- **Response**: `200 OK` with FHIR Composition / Encounter resource JSON.

---

### `GET /api/sessions/{id}`
- **Purpose**: Fetch full session details (patient, answers, documents, OCR entities, summary).
- **Response**: `200 OK` complete session tree.
