import logging
from datetime import datetime, timedelta
from typing import List

from sqlalchemy.orm import Session

from src.exam.model import Exam
from src.exam.service import ExamService
from src.member.model import Member
from src.member.schema import Role
from src.reservation.exception import ReservationNotFound, NotAllowed, ReservationValidationFailed
from src.reservation.model import Reservation, Status
from src.reservation.repository import ReservationRepository
from src.reservation.schema import ReservationCreate, ReservationResponse, ReservationUpdateStatus, ReservationUpdate

logger = logging.getLogger(__name__)


class ReservationService:
    def __init__(self):
        self.repository = ReservationRepository()
        self.exam_service = ExamService()

    def _validate_reservation(self, exam: Exam, people: int):
        if datetime.now() > exam.date - timedelta(days=3):
            raise ReservationValidationFailed()

        if exam.max_people - exam.current_people < people:
            raise ReservationValidationFailed()

    def _validate_authorization(self, member: Member, reservation: Reservation):
        if member.role.value != Role.ADMIN.value and member.id != reservation.member_id:
            raise NotAllowed()

    def create(self, db: Session,
               member: Member,
               reservation_create: ReservationCreate) -> ReservationResponse:
        exam = self.exam_service.get_by_id(db, reservation_create.exam_id)

        self._validate_reservation(exam, reservation_create.people)

        reservation = Reservation(
            exam_id=exam.id,
            member_id=member.id,
            people=reservation_create.people
        )

        return self.repository.save(db, reservation)

    def get_by_id(self, db: Session, member: Member, reservation_id: int) -> ReservationResponse:
        reservation = self.repository.find_by_id(db, reservation_id)

        if not reservation:
            raise ReservationNotFound({reservation_id})

        self._validate_authorization(member, reservation)

        return ReservationResponse.model_validate(reservation)

    def get_all(self, db: Session, member: Member) -> List[ReservationResponse]:
        reservations = self.repository.find_by_member_id(db, member.id)

        return [ReservationResponse.model_validate(reservation) for reservation in reservations]

    def get_all_by_member_id(self, db: Session, member_id: int, ) -> List[ReservationResponse]:
        reservations = self.repository.find_by_member_id(db, member_id)

        return [ReservationResponse.model_validate(reservation) for reservation in reservations]

    def update(self, db: Session,
               member: Member,
               reservation_update: ReservationUpdate) -> ReservationResponse:
        reservation = self.repository.find_by_exam_id_and_member_id(
            db,
            reservation_update.exam_id,
            reservation_update.member_id
        )

        if not reservation:
            raise ReservationNotFound({"exam_id": reservation_update.exam_id,
                                       "member_id": reservation_update.member_id})

        self._validate_authorization(member, reservation)

        reservation.people = reservation_update.people
        updated_reservation = self.repository.save(db, reservation)

        return ReservationResponse.model_validate(updated_reservation)

    def update_status(self, db: Session,
                      reservation_update_status: ReservationUpdateStatus) -> ReservationResponse | None:
        reservation = self.repository.find_by_id(db, reservation_update_status.id)

        if reservation is None:
            raise ReservationNotFound({"id": reservation_update_status.id})

        reservation.status = reservation_update_status.status

        if reservation_update_status.status == Status.CONFIRMED:
            self.exam_service.update_people(db, reservation.exam_id, reservation.people)

        updated_reservation = self.repository.save(db, reservation)

        return ReservationResponse.model_validate(updated_reservation)

    def delete(self, db: Session, member: Member, reservation_id: int) -> None:
        reservation = self.repository.find_by_id(db, reservation_id)

        if reservation is None:
            return ReservationNotFound({reservation_id})

        self._validate_authorization(member, reservation)

        success = self.repository.delete(db, reservation)

        if success and reservation.status == Status.CONFIRMED:
            self.exam_service.update_people(db, reservation.exam_id, -reservation.people)
