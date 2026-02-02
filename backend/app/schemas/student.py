"""Pydantic schemas for Student."""

from pydantic import BaseModel, Field, computed_field


class StudentBase(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    first_name_he: str = Field(default="", max_length=100)
    last_name_he: str = Field(default="", max_length=100)


class StudentCreate(StudentBase):
    pass


class StudentResponse(StudentBase):
    id: int

    @computed_field
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @computed_field
    @property
    def full_name_he(self) -> str:
        return f"{self.first_name_he or ''} {self.last_name_he or ''}".strip()

    model_config = {"from_attributes": True}
