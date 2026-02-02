"""
FastAPI backend: учёт занятий по английскому языку.
Endpoints: / (frontend), /health, /api/*, /metrics.
"""

from contextlib import asynccontextmanager
from pathlib import Path

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.config import get_settings
from app.database import init_db
from app.logging_config import configure_logging
from app.routers import health, lessons, report, students

settings = get_settings()
configure_logging(settings.log_level)
log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: инициализация БД. Shutdown: очистка при необходимости."""
    log.info("Starting application", app_name=settings.app_name)
    init_db()
    log.info("Database initialized")
    yield
    log.info("Shutting down")


app = FastAPI(
    title=settings.app_name,
    description="API учёта занятий по английскому языку для студентов",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS для frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Роутеры
app.include_router(health.router)
app.include_router(students.router)
app.include_router(lessons.router)
app.include_router(report.router)

# Prometheus metrics (endpoint /metrics для сбора Prometheus)
@app.get("/metrics", include_in_schema=False)
def metrics():
    """Метрики в формате Prometheus для мониторинга."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )

# Frontend: статика и стартовая страница
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    def index():
        """Стартовая страница — форма учёта занятий."""
        index_path = STATIC_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return {"service": settings.app_name, "docs": "/docs", "health": "/health"}

    @app.get("/api-info", include_in_schema=False)
    def api_info():
        """Краткая информация об API (для тех, кто не использует /)."""
        return {"service": settings.app_name, "docs": "/docs", "health": "/health", "metrics": "/metrics"}
else:

    @app.get("/")
    def root():
        return {"service": settings.app_name, "docs": "/docs", "health": "/health", "metrics": "/metrics"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
