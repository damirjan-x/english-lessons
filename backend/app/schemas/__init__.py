"""Pydantic schemas for API."""

from app.schemas.lesson import LessonRecordCreate, LessonRecordResponse
from app.schemas.student import StudentCreate, StudentResponse

__all__ = [
    "StudentCreate",
    "StudentResponse",
    "LessonRecordCreate",
    "LessonRecordResponse",
]
