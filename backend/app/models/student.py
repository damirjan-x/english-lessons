"""Student model — данные студентов для выпадающего списка."""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Student(Base):
    """Студент: имя и фамилия на русском и на иврите."""

    __tablename__ = "students"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # Русский
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    # Иврит
    first_name_he = Column(String(100), default="")
    last_name_he = Column(String(100), default="")

    lessons = relationship("LessonRecord", back_populates="student")

    def __repr__(self) -> str:
        return f"<Student(id={self.id}, {self.first_name} {self.last_name})>"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name_he(self) -> str:
        return f"{self.first_name_he or ''} {self.last_name_he or ''}".strip()
