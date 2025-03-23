from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


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


class MemberResponse(BaseModel):
    id: int
    username: str
    role: Role
    created_at: datetime
    modified_at: datetime

    model_config = {
        'from_attributes': True
    }


class LoginResponse(BaseModel):
    access_token: str


class MemberLogin(BaseModel):
    username: str
    password: str
