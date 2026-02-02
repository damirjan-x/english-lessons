"""Health check endpoint для Kubernetes и мониторинга."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.deps import get_db

router = APIRouter(tags=["health"])


@router.get("/health", summary="Health check")
def health(db: Session = Depends(get_db)):
    """
    Проверка работоспособности сервиса и доступности БД.
    Используется Kubernetes liveness/readiness и мониторингом.
    """
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "database": db_status,
    }
