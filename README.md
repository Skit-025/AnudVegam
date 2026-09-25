# MediKiosk (SIH26047) - Patient Case-Taking Software

## Project Overview
MediKiosk is an AI-assisted digital intake kiosk for outpatient departments (OPDs) in Indian public healthcare hospitals. It streamlines patient identification, informed consent, symptom case-taking (Allopathic & AYUSH), prescription/lab report scanning via OCR, and automated clinical summary generation with doctor-in-the-loop review and mocked ABDM/FHIR export.

## Architecture
- **Frontend**: React + Vite + Tailwind CSS (`frontend/`)
- **Main Backend Orchestrator**: Python + FastAPI + SQLAlchemy + Pydantic (`backend/`)
- **AI Microservices** (`ai-services/`):
  - **Dialogue Service** (`ai-services/dialogue/`): Rule-based question branching and red-flag screening.
  - **OCR Service** (`ai-services/ocr/`): Document image preprocessing, Tesseract OCR, and regex/dictionary medical entity extraction.
  - **Summarizer Service** (`ai-services/summarizer/`): Structured clinical note drafting using prompt templates and LLMs.
- **Database**: PostgreSQL with 9 relational tables (`database/`)
- **Documentation**: API contracts and architecture specifications (`docs/`)

## Service Map & Port Allocation
| Service | Technology | Port | Description |
|---|---|---|---|
| Frontend | React + Vite | 3000 | Kiosk UI & Doctor Review Portal |
| Main Backend | FastAPI | 8000 | Core Orchestrator & Database API |
| Dialogue AI | FastAPI | 8001 | Medical Question Tree & Red-Flag Service |
| OCR AI | FastAPI | 8002 | Document Image Preprocessing & Entity Extractor |
| Summarizer AI | FastAPI | 8003 | Clinical Case Note LLM Drafter |
| PostgreSQL | PostgreSQL 16 | 5432 | Primary Relational Database |

## Folder Structure
```
medikiosk/
├── frontend/                # React + Vite + Tailwind UI
├── backend/                 # Main Python FastAPI Orchestrator
├── ai-services/
│   ├── dialogue/            # Question tree & red-flag detection
│   ├── ocr/                 # Preprocessing & medical entity extraction
│   └── summarizer/          # Prompt-based clinical summary generation
├── database/                # Schema migrations and seed data
├── docs/                    # Architecture and API contracts
└── docker-compose.yml       # Multi-container orchestration
```

## Vercel Deployment

MediKiosk is pre-configured for seamless deployment to [Vercel](https://vercel.com):
- **Frontend Directory**: `frontend/`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **SPA Rewrites**: Configured via [vercel.json](vercel.json) to support client-side routing on all pages.

For step-by-step instructions, see [docs/VERCEL_DEPLOYMENT.md](docs/VERCEL_DEPLOYMENT.md).

## Render Deployment (Backend & Database)

MediKiosk Backend is configured for deployment to [Render](https://render.com):
- **Service Type**: Web Service (Python 3)
- **Root Directory**: `backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Database**: Render Managed PostgreSQL

For step-by-step instructions, see [docs/RENDER_DEPLOYMENT.md](docs/RENDER_DEPLOYMENT.md).

