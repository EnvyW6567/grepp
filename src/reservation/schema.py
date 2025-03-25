from datetime import datetime

from pydantic import BaseModel

from src.reservation.model import Status


class ReservationBase(BaseModel):
    exam_id: int
    people: int


class ReservationCreate(ReservationBase):
    pass


class ReservationUpdate(ReservationBase):
    pass


class ReservationUpdateStatus(BaseModel):
    id: int
    status: Status


class ReservationResponse(BaseModel):
    id: int
    status: Status
    people: int
    created_at: datetime
    modified_at: datetime

    model_config = {
        'from_attributes': True
    }
