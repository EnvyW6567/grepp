from typing import List

from fastapi import APIRouter, status, Depends
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
def create(reservationCreate: ReservationCreate,
           db: Session = Depends(get_db),
           member: Member = Depends(get_current_member)) -> ReservationResponse:
    return reservation_service.create(db, member, reservationCreate)


@router.get("/", response_model=List[ReservationResponse], status_code=status.HTTP_200_OK)
def get_all(db: Session = Depends(get_db),
            member: Member = Depends(get_current_member)) -> List[ReservationResponse]:
    return reservation_service.get_all(db, member)


@router.get("/{reservation_id}", response_model=ReservationResponse, status_code=status.HTTP_200_OK)
def get_by_id(reservation_id: int,
              db: Session = Depends(get_db),
              member: Member = Depends(get_current_member)) -> ReservationResponse:
    return reservation_service.get_by_id(db, member, reservation_id)


@router.put("/", response_model=ReservationResponse, status_code=status.HTTP_200_OK)
def update(reservation_update: ReservationUpdate,
           db: Session = Depends(get_db),
           member: Member = Depends(get_current_member)) -> ReservationResponse:
    return reservation_service.update(db, member, reservation_update)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete(reservation_id: int,
           db: Session = Depends(get_db),
           member: Member = Depends(get_current_member)):
    reservation_service.delete(db, member, reservation_id)
