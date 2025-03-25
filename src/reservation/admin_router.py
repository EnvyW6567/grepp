from typing import List

from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from src.auth.dependencies import get_admin_member
from src.db.db import get_db
from src.member.model import Member
from src.reservation.schema import ReservationResponse, ReservationUpdate, ReservationUpdateStatus
from src.reservation.service import ReservationService

admin_router = APIRouter(
    prefix="/admin/reservation",
    tags=["reservation"],
    responses={404: {"description": "Not found"}},
)

reservation_service = ReservationService()


@admin_router.get("/{member_id}", response_model=List[ReservationResponse], status_code=status.HTTP_200_OK)
def get_reservations_by_member_id(member_id: int,
                                  db: Session = Depends(get_db),
                                  admin: Member = Depends(get_admin_member)) -> List[ReservationResponse]:
    return reservation_service.get_all_by_member_id(db, member_id)


@admin_router.put("/", status_code=status.HTTP_200_OK)
def update_reservation(reservation_update: ReservationUpdate,
                       db: Session = Depends(get_db),
                       admin: Member = Depends(get_admin_member)) -> ReservationResponse:
    return reservation_service.update(db, admin, reservation_update)


@admin_router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_reservation(reservation_id: int,
                       db: Session = Depends(get_db),
                       admin: Member = Depends(get_admin_member)):
    reservation_service.delete(db, admin, reservation_id)


@admin_router.put("/status", response_model=ReservationResponse, status_code=status.HTTP_200_OK)
def update_reservation_status(reservation_update_status: ReservationUpdateStatus,
                              db: Session = Depends(get_db),
                              admin: Member = Depends(get_admin_member)) -> ReservationResponse:
    return reservation_service.update_status(db, reservation_update_status)
