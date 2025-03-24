from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.auth.dependencies import get_admin_member
from src.db.db import get_db
from src.exam.schema import ExamResponse, ExamCreate
from src.exam.service import ExamService
from src.member.model import Member

router = APIRouter(
    prefix="/exams",
    tags=["exams"],
    responses={404: {"description": "Not found"}},
)

admin_router = APIRouter(
    prefix="/admin/exams",
    tags=["admin", "exams"],
    responses={404: {"description": "Not found"}},
)

exam_service = ExamService()


@router.get("/", response_model=List[ExamResponse])
def get_all_exams(db: Session = Depends(get_db)):
    return exam_service.get_all(db)


@router.get("/{exam_id}", response_model=ExamResponse)
def get_exam(
        exam_id: int,
        db: Session = Depends(get_db),
):
    exam = exam_service.get_by_id(db, exam_id)

    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    return exam


@admin_router.post("/", response_model=ExamResponse)
def create_exam(
        examCreate: ExamCreate,
        db: Session = Depends(get_db),
        admin: Member = Depends(get_admin_member),
):
    return exam_service.create(db, admin, examCreate)


@admin_router.get("/", response_model=list[ExamResponse])
def get_all_exams(
        db: Session = Depends(get_db),
        admin: Member = Depends(get_admin_member)  # 로깅 용도로 사용 예정
):
    return exam_service.get_all(db)


@admin_router.get("/{exam_id}", response_model=ExamResponse)
def get_any_exam(
        exam_id: int,
        db: Session = Depends(get_db),
        admin: Member = Depends(get_admin_member)  # 로깅 용도로 사용 예정
):
    exam = exam_service.get_by_id(db, exam_id)

    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    return exam


@admin_router.delete("/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_any_exam(
        exam_id: int,
        db: Session = Depends(get_db),
        admin: Member = Depends(get_admin_member)
):
    success = exam_service.delete(db, exam_id)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete exam")

    return None
