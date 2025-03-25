from typing import List

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session

from src.auth.dependencies import get_current_member
from src.db.db import get_db
from src.member.model import Member
from src.reservation.schema import ReservationCreate, ReservationResponse, ReservationUpdate
from src.reservation.service import ReservationService

router = APIRouter(
    prefix="/reservation",
    tags=["reservation"],
    responses={404: {"description": "Not found"}},
)

reservation_service = ReservationService()


@router.post("/", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
def create_reservation(reservationCreate: ReservationCreate,
                       db: Session = Depends(get_db),
                       member: Member = Depends(get_current_member)) -> ReservationResponse:
    reservationResponse = reservation_service.create(db, member, reservationCreate)

    if reservationResponse is None:
        raise HTTPException(status_code=400, detail="Could not create reservation")

    return reservationResponse


@router.get("/", response_model=List[ReservationResponse], status_code=status.HTTP_200_OK)
def get_reservations(db: Session = Depends(get_db),
                     member: Member = Depends(get_current_member)) -> List[ReservationResponse]:
    return reservation_service.get_all(db, member)


@router.get("/{reservation_id}", response_model=ReservationResponse, status_code=status.HTTP_200_OK)
def get_reservation(reservation_id: int,
                    db: Session = Depends(get_db),
                    member: Member = Depends(get_current_member)) -> ReservationResponse:
    return reservation_service.get_by_id(db, member, reservation_id)


@router.put("/", response_model=ReservationResponse, status_code=status.HTTP_200_OK)
def update_reservation(reservation_update: ReservationUpdate,
                       db: Session = Depends(get_db),
                       member: Member = Depends(get_current_member)) -> ReservationResponse:
    return reservation_service.update(db, member, reservation_update)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_reservation(reservation_id: int,
                       db: Session = Depends(get_db),
                       member: Member = Depends(get_current_member)):
    reservation_service.delete(db, member, reservation_id)
