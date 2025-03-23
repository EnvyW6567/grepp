from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from typing import Optional


class Role(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"


class MemberBase(BaseModel):
    username: str


class MemberCreate(MemberBase):
    password: str
    role: Role = Role.USER


class MemberUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[Role] = None


class MemberInDB(MemberBase):
    id: int
    role: Role
    created_at: datetime
    modified_at: datetime

    class Config:
        orm_mode = True


class MemberResponse(BaseModel):
    id: int
    username: str
    role: Role
    created_at: datetime
    modified_at: datetime

    model_config = {
        'from_attributes': True
    }
