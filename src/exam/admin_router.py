from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.auth.dependencies import get_admin_member
from src.db.db import get_db
from src.exam.schema import ExamCreate, ExamResponse
from src.exam.service import ExamService
from src.member.model import Member

admin_router = APIRouter(
    prefix="/admin/exams",
    tags=["admin", "exams"],
    responses={404: {"description": "Not found"}},
)

exam_service = ExamService()


@admin_router.post("/", response_model=ExamResponse)
def create(
        examCreate: ExamCreate,
        db: Session = Depends(get_db),
        admin: Member = Depends(get_admin_member),
):
    return exam_service.create(db, admin, examCreate)


@admin_router.get("/", response_model=list[ExamResponse])
def get_all(
        db: Session = Depends(get_db),
        admin: Member = Depends(get_admin_member)
):
    return exam_service.get_all(db)


@admin_router.get("/{exam_id}", response_model=ExamResponse)
def get(
        exam_id: int,
        db: Session = Depends(get_db),
        admin: Member = Depends(get_admin_member)
):
    exam = exam_service.get_by_id(db, exam_id)

    return exam


@admin_router.delete("/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
        exam_id: int,
        db: Session = Depends(get_db),
        admin: Member = Depends(get_admin_member)
) -> None:
    exam_service.delete(db, exam_id)
