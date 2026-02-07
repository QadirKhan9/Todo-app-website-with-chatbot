from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config.settings import get_settings
settings = get_settings()
import os


# Handle different database types
db_url = settings.DATABASE_URL
if db_url.startswith("sqlite"):
    # For SQLite, disable pooling which can cause issues
    engine = create_engine(
        db_url,
        echo=settings.DATABASE_ECHO,  # Enable SQL logging in debug mode
        connect_args={"check_same_thread": False},  # Required for SQLite
        pool_pre_ping=True,
        pool_recycle=300,
    )
else:
    # For other databases (PostgreSQL, MySQL, etc.)
    engine = create_engine(
        db_url,
        echo=settings.DATABASE_ECHO,  # Enable SQL logging in debug mode
        pool_pre_ping=True,
        pool_recycle=300,
        # Add additional args for PostgreSQL
        pool_size=20,
        max_overflow=0,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Async database setup for future use
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

# Only set up async engine for PostgreSQL
if db_url.startswith("postgresql"):
    async_db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
    async_engine = create_async_engine(async_db_url, echo=settings.DATABASE_ECHO)
    AsyncSessionLocal = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
else:
    # For SQLite and other sync drivers, we'll set up placeholders
    async_engine = None
    AsyncSessionLocal = None


async def get_async_db():
    if AsyncSessionLocal is None:
        raise RuntimeError("Async database session not available for this database type")
    async with AsyncSessionLocal() as session:
        yield session