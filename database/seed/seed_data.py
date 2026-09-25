"""
Database Seed Script - MediKiosk Test Scenarios & Reference Data
================================================================

File Purpose:
-------------
Populates the PostgreSQL / SQLite database with seed patients, initial demo scenarios
(normal case, red-flag case, and messy prescription case), and consent records.
"""

import asyncio
import os
import sys

# Ensure backend path is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.dependencies import AsyncSessionLocal, init_db
from app.models.patient import PatientModel
from app.models.consent import ConsentModel
from app.models.session import SessionModel
from app.models.response import HistoryResponseModel
from sqlalchemy import select


SAMPLE_PATIENTS = [
    {
        "id": "p-ramesh-001",
        "name": "Ramesh Kumar",
        "abha_id": "91-1234-5678-9012",
        "age": 45,
        "gender": "MALE",
        "phone": "9876543210",
        "preferred_language": "hi",
        "consent": "मैं ओपीडी ट्रायज के लिए अपने लक्षण और स्वास्थ्य विवरण एकत्र करने की अनुमति देता हूं।",
        "mode": "ALLOPATHIC"
    },
    {
        "id": "p-sunita-002",
        "name": "Sunita Devi",
        "abha_id": "91-9876-5432-1098",
        "age": 58,
        "gender": "FEMALE",
        "phone": "9123456780",
        "preferred_language": "en",
        "consent": "I authorize digital case-taking and triage for emergency and OPD evaluation.",
        "mode": "ALLOPATHIC"
    },
    {
        "id": "p-anil-003",
        "name": "Anil Deshmukh",
        "abha_id": "91-5555-4444-3333",
        "age": 34,
        "gender": "MALE",
        "phone": "9988776655",
        "preferred_language": "mr",
        "consent": "मी ओपीडी ट्रायजसाठी माझे आरोग्य आणि लक्षणांची माहिती देण्यास संमती देतो.",
        "mode": "AYUSH"
    }
]


async def seed_database():
    """
    Execute real database seeding routine.
    """
    print("Initializing database tables...")
    await init_db()

    async with AsyncSessionLocal() as session:
        for p in SAMPLE_PATIENTS:
            stmt = select(PatientModel).where(PatientModel.abha_id == p["abha_id"])
            existing = (await session.execute(stmt)).scalar_one_or_none()

            if not existing:
                # 1. Create Patient
                patient = PatientModel(
                    id=p["id"],
                    abha_id=p["abha_id"],
                    name=p["name"],
                    age=p["age"],
                    gender=p["gender"],
                    phone=p["phone"],
                    preferred_language=p["preferred_language"]
                )
                session.add(patient)

                # 2. Create Consent
                consent = ConsentModel(
                    patient_id=p["id"],
                    consent_granted=True,
                    consent_text=p["consent"],
                    language=p["preferred_language"]
                )
                session.add(consent)

                # 3. Create Sample Initial Session
                encounter = SessionModel(
                    patient_id=p["id"],
                    mode=p["mode"],
                    status="ACTIVE"
                )
                session.add(encounter)
                print(f"Seeded Patient: {p['name']} ({p['mode']} mode)")

        await session.commit()
    print("Database seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())
