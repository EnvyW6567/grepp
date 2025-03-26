from datetime import datetime

from pydantic import BaseModel, Field

from src.reservation.model import Status


class ReservationBase(BaseModel):
    people: int = Field(ge=1, le=50000)


class ReservationCreate(ReservationBase):
    exam_id: int


class ReservationUpdate(ReservationBase):
    id: int


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
