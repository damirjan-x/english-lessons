"""API студентов — для выпадающего списка на frontend."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import Student
from app.schemas import StudentCreate, StudentResponse

router = APIRouter(prefix="/api/students", tags=["students"])


@router.get("", response_model=list[StudentResponse])
def list_students(db: Session = Depends(get_db)):
    """Список студентов (имя и фамилия) для выпадающего списка."""
    return db.query(Student).order_by(Student.last_name, Student.first_name).all()


@router.post("", response_model=StudentResponse, status_code=201)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """Создание студента (для администрирования/начального наполнения)."""
    obj = Student(
        first_name=student.first_name,
        last_name=student.last_name,
        first_name_he=student.first_name_he or "",
        last_name_he=student.last_name_he or "",
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db)):
    """Получить студента по ID."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student
