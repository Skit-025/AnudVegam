"""
SQLAlchemy Base & Metadata Definition
=====================================

File Purpose:
-------------
Defines the common DeclarativeBase and timestamp mixin for all PostgreSQL ORM models.

Connected to:
-------------
- All models under `backend/app/models/` inherit from `Base`.
- Used by Alembic migrations in `backend/alembic/env.py`.
"""

import uuid
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy 2.0 ORM models."""
    pass


class TimestampMixin:
    """Provides created_at and updated_at audit timestamps."""
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
