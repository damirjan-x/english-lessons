"""Lesson record model — данные по занятиям за месяц/год."""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class LessonRecord(Base):
    """
    Запись занятий за выбранный месяц и год по студенту.
    Поля на английском (E), часы 1–12.
    """

    __tablename__ = "lesson_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)  # 1–12

    # English (до 255 символов)
    grammar_e = Column(String(255), default="")
    reading_e = Column(String(255), default="")
    speaking_e = Column(String(255), default="")
    writing_e = Column(String(255), default="")

    # Количество часов обучения (1–12)
    hours_studied = Column(Integer, nullable=False, default=1)

    student = relationship("Student", back_populates="lessons")

    def __repr__(self) -> str:
        return f"<LessonRecord(id={self.id}, student_id={self.student_id}, {self.year}-{self.month})>"
