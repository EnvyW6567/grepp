from datetime import datetime

from pydantic import BaseModel, Field


class ExamBase(BaseModel):
    date: datetime
    description: str
    current_people: int = Field(default=0, ge=0)
    max_people: int = Field(default=50000, ge=1)


class ExamCreate(ExamBase):
    pass


class ExamResponse(ExamBase):
    id: int
    member_id: int
    created_at: datetime

    model_config = {
        'from_attributes': True
    }
