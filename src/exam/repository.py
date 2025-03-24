from typing import List

from sqlalchemy.orm import Session

from src.exam.model import Exam


class ExamRepository:
    def find_all(self, db: Session) -> List[Exam]:
        return db.query(Exam).all()

    def find_by_id(self, db: Session, exam_id: int) -> Exam | None:
        return db.query(Exam).filter(Exam.id == exam_id).first()

    def find_by_member_id(self, db: Session, member_id: int) -> List[Exam]:
        return db.query(Exam).filter(Exam.member_id == member_id).all()

    def save(self, db: Session, exam: Exam) -> Exam:
        db.add(exam)
        db.commit()
        db.refresh(exam)
        return exam

    def delete(self, db: Session, exam: Exam) -> bool:
        db.delete(exam)
        db.commit()
        return True
