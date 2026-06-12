import os

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker
)

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.strip()

    if (
        (DATABASE_URL.startswith('"') and DATABASE_URL.endswith('"'))
        or (DATABASE_URL.startswith("'") and DATABASE_URL.endswith("'"))
    ):
        DATABASE_URL = DATABASE_URL[1:-1]

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is not set or is empty. "
        "Set it in your deployment platform's Variables section."
    )

if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql+psycopg2://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)

engine = create_async_engine(
    DATABASE_URL,
    echo=True
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False
)
