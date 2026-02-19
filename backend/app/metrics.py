"""Регистрация метрик Prometheus для приложения."""

import time
from contextlib import contextmanager
from typing import Generator

from prometheus_client import Counter, Histogram

# HTTP
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)
http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

# БД
db_request_duration_seconds = Histogram(
    "db_request_duration_seconds",
    "Database request duration in seconds",
    ["operation"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
)
db_errors_total = Counter(
    "db_errors_total",
    "Total database errors",
    ["operation"],
)

# Бизнес
lessons_saved_total = Counter(
    "lessons_saved_total",
    "Total lesson records saved",
)
reports_generated_total = Counter(
    "reports_generated_total",
    "Total PDF reports generated",
)


@contextmanager
def track_db_operation(operation: str) -> Generator[None, None, None]:
    """Контекстный менеджер: замер времени и учёт ошибок БД."""
    start = time.perf_counter()
    try:
        yield
    except Exception:
        db_errors_total.labels(operation=operation).inc()
        raise
    finally:
        db_request_duration_seconds.labels(operation=operation).observe(
            time.perf_counter() - start
        )
