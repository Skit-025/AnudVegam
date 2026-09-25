"""
Alembic Environment Migration Configuration
============================================

File Purpose:
-------------
Controls database migration generation and schema execution for SQLAlchemy 2.0 models.

Connected to:
-------------
- `backend/app/models/`: Imports Base.metadata to track schema diffs for all 9 tables.
- `backend/app/core/config.py`: Injects database URL.
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from backend.app.core.config import settings
from backend.app.models.base import Base
# Import all models so metadata is populated
from backend.app.models import (
    PatientModel,
    ConsentModel,
    SessionModel,
    HistoryResponseModel,
    DocumentModel,
    ExtractedEntityModel,
    CaseSummaryModel,
    FHIRExportModel
)

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    # Step 1: Configure migration context with target metadata.
    # Step 2: Generate SQL script.
    pass

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Step 1: Connect to database engine.
    # Step 2: Run migrations inside transaction.
    pass

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
