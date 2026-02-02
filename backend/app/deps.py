"""FastAPI dependencies (DB session, etc.)."""

from typing import Generator

from sqlalchemy.orm import Session

from app.database import get_session_factory


def get_db() -> Generator[Session, None, None]:
    """Dependency that yields a DB session and closes it after request."""
    SessionLocal = get_session_factory()
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
