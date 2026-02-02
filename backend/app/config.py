"""Application configuration from environment (12-factor, Kubernetes-friendly)."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "english-lessons-api"
    debug: bool = False
    log_level: str = "INFO"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # MySQL
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "app"
    mysql_password: str = ""
    mysql_database: str = "english_lessons"

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )

    # Paths (for Docker/K8s: templates and temp files)
    templates_dir: str = "templates"
    report_template_name: str = "report_template.docx"
    temp_dir: str = "/tmp"


@lru_cache
def get_settings() -> Settings:
    return Settings()
