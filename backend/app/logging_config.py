"""
Настройка логирования для Loki/Promtail (JSON-формат).
Структурированные логи удобны для сбора в Loki и поиска.
"""

import logging
import sys

import structlog


def configure_logging(log_level: str = "INFO") -> None:
    """Настройка structlog с JSON-выводом для Loki."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer() if _is_json_env() else structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


def _is_json_env() -> bool:
    """В контейнере/K8s логируем в JSON для Loki."""
    import os
    return os.environ.get("LOG_FORMAT", "").lower() == "json"
