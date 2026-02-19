"""API формирования PDF-отчёта (Print report)."""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session, joinedload

from app.deps import get_db
from app.metrics import reports_generated_total
from app.models import LessonRecord
from app.services.report import render_docx_and_convert_to_pdf

router = APIRouter(prefix="/api/report", tags=["report"])


@router.get("/pdf", response_class=Response)
def print_report(
    student_id: int = Query(..., description="ID студента"),
    year: int = Query(..., description="Год"),
    month: int = Query(..., ge=1, le=12, description="Месяц (1–12)"),
    db: Session = Depends(get_db),
):
    """
    Формирует PDF-отчёт по выбранному студенту, месяцу и году.
    Используется шаблон .docx с подстановкой данных из БД.
    Файл возвращается для скачивания.
    """
    record = (
        db.query(LessonRecord)
        .options(joinedload(LessonRecord.student))
        .filter(
            LessonRecord.student_id == student_id,
            LessonRecord.year == year,
            LessonRecord.month == month,
        )
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=404,
            detail="No lesson data found for this student, year and month",
        )

    try:
        pdf_bytes = render_docx_and_convert_to_pdf(record)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Report template missing: {e}")
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {e}")
    except Exception as e:
        err_msg = str(e).replace("\n", " ").strip() or type(e).__name__
        raise HTTPException(status_code=500, detail=f"Report error: {err_msg}")

    reports_generated_total.inc()

    # Имя файла только ASCII — заголовки HTTP кодируются в latin-1
    filename = f"report_{record.student_id}_{year}_{month:02d}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
