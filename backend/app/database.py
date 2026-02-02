"""Database connection and session management (MySQL via SQLAlchemy)."""

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import get_settings

Base = declarative_base()
_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=settings.debug,
        )
    return _engine


def get_session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_engine(),
        )
    return _SessionLocal


def init_db() -> None:
    """Create tables if they do not exist and add start data (students) if empty."""
    from app.models import Student, lesson, student  # noqa: F401

    Base.metadata.create_all(bind=get_engine())

    # Стартовые данные: ученики (русский + иврит), только если таблица пуста
    SessionLocal = get_session_factory()
    with SessionLocal() as session:
        if session.scalar(select(func.count()).select_from(Student)) == 0:
            for first_name, last_name, first_name_he, last_name_he in [
                ("Адели", "Рабинович", "אדל", "רבינוביץ'"),
                ("Ривки", "Забродски", "רבקה", "זברודסקי"),
                ("Ципоры", "Херман", "ציפורה", "הרמן"),
            ]:
                session.add(
                    Student(
                        first_name=first_name,
                        last_name=last_name,
                        first_name_he=first_name_he,
                        last_name_he=last_name_he,
                    )
                )
            session.commit()
