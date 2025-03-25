from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.db import get_db
from src.exam.schema import ExamResponse
from src.exam.service import ExamService

router = APIRouter(
    prefix="/exams",
    tags=["exams"],
    responses={404: {"description": "Not found"}},
)

exam_service = ExamService()


@router.get("/", response_model=List[ExamResponse])
def get_all(db: Session = Depends(get_db)):
    return exam_service.get_all(db)


@router.get("/{exam_id}", response_model=ExamResponse)
def get(
        exam_id: int,
        db: Session = Depends(get_db)
):
    return exam_service.get_by_id(db, exam_id)
