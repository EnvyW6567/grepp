import enum

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.sql import func

from src.db.db import Base


class Status(enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    DENIED = "DENIED"


class ReservationHistory(Base):
    __tablename__ = "reservation_history"

    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey("member.id"), index=True, nullable=False)
    reservation_id = Column(Integer, ForeignKey("reservation.id"), nullable=False)
    people = Column(Integer, nullable=False)
    status = Column(Enum(Status), default=Status.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
