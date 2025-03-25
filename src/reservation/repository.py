from typing import List

from sqlalchemy.orm import Session

from src.reservation.model import Reservation


class ReservationRepository:
    def find_by_member_id(self, db: Session, member_id: int) -> List[Reservation]:
        return db.query(Reservation).filter(Reservation.member_id == member_id).all()

    def find_by_id(self, db: Session, id: int) -> Reservation | None:
        return db.query(Reservation).filter(Reservation.id == id).first()

    def find_by_exam_id_and_member_id(self, db: Session, exam_id: int,
                                      member_id: int) -> Reservation | None:
        return db.query(Reservation).filter(Reservation.exam_id == exam_id,
                                            Reservation.member_id == member_id).first()

    def save(self, db: Session, reservationHistory: Reservation) -> Reservation:
        db.add(reservationHistory)
        db.commit()
        db.refresh(reservationHistory)
        
        return reservationHistory

    def delete(self, db: Session, reservation: Reservation) -> bool:
        db.delete(reservation)
        db.commit()

        return True
