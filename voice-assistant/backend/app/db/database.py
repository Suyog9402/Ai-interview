import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from ..core.config import settings

logger = logging.getLogger(__name__)


def create_db_engine():
    """Create database engine with automatic graceful SQLite fallback if PostgreSQL is offline."""
    if "postgresql" in settings.database_url:
        try:
            eng = create_engine(
                settings.database_url,
                pool_pre_ping=True,
                pool_size=settings.database_pool_size,
                max_overflow=settings.database_max_overflow,
                pool_timeout=2,
                pool_recycle=settings.database_pool_recycle
            )
            with eng.connect() as conn:
                pass
            logger.info("Connected to PostgreSQL database successfully.")
            return eng
        except Exception as e:
            logger.warning(
                f"PostgreSQL server not reachable at {settings.database_url} ({e}). "
                "Falling back to local SQLite database (interview_assistant.db)."
            )
            sqlite_url = "sqlite:///./interview_assistant.db"
            return create_engine(sqlite_url, connect_args={"check_same_thread": False})
    elif "sqlite" in settings.database_url:
        return create_engine(settings.database_url, connect_args={"check_same_thread": False})
    else:
        return create_engine(settings.database_url)


engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()