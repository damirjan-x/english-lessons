"""API занятий — сохранение и чтение данных по занятиям."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import LessonRecord, Student
from app.schemas import LessonRecordCreate, LessonRecordResponse

router = APIRouter(prefix="/api/lessons", tags=["lessons"])


@router.post("", response_model=LessonRecordResponse, status_code=201)
def send_lesson_data(data: LessonRecordCreate, db: Session = Depends(get_db)):
    """
    Отправка данных занятия (Send data).
    Создаёт или обновляет запись по студенту, году и месяцу.
    """
    student = db.query(Student).filter(Student.id == data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    existing = (
        db.query(LessonRecord)
        .filter(
            LessonRecord.student_id == data.student_id,
            LessonRecord.year == data.year,
            LessonRecord.month == data.month,
        )
        .first()
    )

    if existing:
        existing.grammar_e = data.grammar_e
        existing.reading_e = data.reading_e
        existing.speaking_e = data.speaking_e
        existing.writing_e = data.writing_e
        existing.hours_studied = data.hours_studied
        db.commit()
        db.refresh(existing)
        return existing

    record = LessonRecord(
        student_id=data.student_id,
        year=data.year,
        month=data.month,
        grammar_e=data.grammar_e,
        reading_e=data.reading_e,
        speaking_e=data.speaking_e,
        writing_e=data.writing_e,
        hours_studied=data.hours_studied,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=LessonRecordResponse | None)
def get_lesson_for_month(
    student_id: int = Query(...),
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
):
    """Получить данные занятия по студенту, году и месяцу (для заполнения формы)."""
    return (
        db.query(LessonRecord)
        .filter(
            LessonRecord.student_id == student_id,
            LessonRecord.year == year,
            LessonRecord.month == month,
        )
        .first()
    )
