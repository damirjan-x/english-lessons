"""Pydantic schemas for LessonRecord."""

from pydantic import BaseModel, Field


class LessonRecordBase(BaseModel):
    student_id: int
    year: int
    month: int = Field(..., ge=1, le=12)
    grammar_e: str = Field(default="", max_length=255)
    reading_e: str = Field(default="", max_length=255)
    speaking_e: str = Field(default="", max_length=255)
    writing_e: str = Field(default="", max_length=255)
    hours_studied: int = Field(default=1, ge=1, le=12)


class LessonRecordCreate(LessonRecordBase):
    pass


class LessonRecordResponse(LessonRecordBase):
    id: int

    model_config = {"from_attributes": True}
