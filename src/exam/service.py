from typing import List

from sqlalchemy.orm import Session

from src.exam.exception import ExamCapacityExceededError, ExamNotFound
from src.exam.model import Exam
from src.exam.repository import ExamRepository
from src.exam.schema import ExamCreate, ExamResponse
from src.member.model import Member


class ExamService:
    def __init__(self):
        self.repository = ExamRepository()

    def get_all(self, db: Session) -> List[ExamResponse]:
        exams = self.repository.find_all(db)

        return [ExamResponse.model_validate(exam) for exam in exams]

    def get_by_id(self, db: Session, exam_id: int) -> ExamResponse:
        exam = self.repository.find_by_id(db, exam_id)

        if not exam:
            raise ExamNotFound(exam_id)

        return ExamResponse.model_validate(exam)

    def get_by_member_id(self, db: Session, member_id: int) -> List[ExamResponse]:
        exams = self.repository.find_by_member_id(db, member_id)

        return [ExamResponse.model_validate(exam) for exam in exams]

    def create(self, db: Session, member: Member, exam_create: ExamCreate) -> ExamResponse:
        if exam_create.current_people > exam_create.max_people:
            raise ExamCapacityExceededError()

        exam = Exam(
            member_id=member.id,
            date=exam_create.date,
            description=exam_create.description,
            current_people=exam_create.current_people,
            max_people=exam_create.max_people
        )
        saved_exam = self.repository.save(db, exam)

        return ExamResponse.model_validate(saved_exam)

    def delete(self, db: Session, exam_id: int) -> bool:
        exam = self.repository.find_by_id(db, exam_id)
        if not exam:
            raise ExamNotFound(exam_id)

        return self.repository.delete(db, exam)

    def update_people(self, db: Session, exam_id: int, people: int):
        exam = self.repository.find_by_id(db, exam_id)
        if not exam:
            raise ExamNotFound(exam_id)

        exam.current_people = people

        return self.repository.save(db, exam)
