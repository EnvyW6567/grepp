from sqlalchemy import Column, Integer, DateTime, ForeignKey, String
from sqlalchemy.sql import func

from src.db.db import Base


class Exam(Base):
    __tablename__ = "exam"

    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey("member.id"), nullable=False)
    description = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    current_people = Column(Integer, default=0, nullable=False)
    max_people = Column(Integer, default=50000, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    modified_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
