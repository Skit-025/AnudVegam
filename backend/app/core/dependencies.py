"""
Main Backend - FastAPI Dependency Injection Hub
===============================================

File Purpose:
-------------
Defines reusable dependency providers for database sessions, schema initialization,
authentication guards, and HTTP clients communicating with internal AI microservices.

What it does:
-------------
1. Creates async SQLAlchemy database engine and session factory.
2. Initializes all database tables (`init_db`) on application startup.
3. Injects initialized AI service HTTP client instances (Dialogue, OCR, Summarizer).
"""

from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from .config import settings
from .security import SecurityManager
from ..models.base import Base
# Import all models to ensure metadata is fully populated for table creation
from ..models.patient import PatientModel
from ..models.consent import ConsentModel
from ..models.session import SessionModel
from ..models.response import HistoryResponseModel
from ..models.document import DocumentModel
from ..models.entity import ExtractedEntityModel
from ..models.summary import CaseSummaryModel
from ..models.fhir import FHIRExportModel
from ..clients.dialogue_client import DialogueClient
from ..clients.ocr_client import OCRClient
from ..clients.summarizer_client import SummarizerClient

# Engine configuration supporting SQLite or PostgreSQL
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    connect_args=connect_args
)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

security_manager = SecurityManager()


async def init_db():
    """
    Initialize all relational database tables on startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency provider yielding an asynchronous SQLAlchemy database session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_dialogue_client() -> DialogueClient:
    return DialogueClient(base_url=settings.DIALOGUE_SERVICE_URL)


def get_ocr_client() -> OCRClient:
    return OCRClient(base_url=settings.OCR_SERVICE_URL)


def get_summarizer_client() -> SummarizerClient:
    return SummarizerClient(base_url=settings.SUMMARIZER_SERVICE_URL)
