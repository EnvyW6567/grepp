from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.core.security.security import decode_token
from src.db.db import get_db
from src.member.model import Member, Role
from src.member.repository import MemberRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="members/login")

member_repository = MemberRepository()


async def get_current_member(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Member:
    token_data = decode_token(token)

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    member = member_repository.find_by_id(db, token_data.id)
    if member is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return member


async def get_current_active_member(current_member: Member = Depends(get_current_member)) -> Member:
    return current_member


async def get_admin_member(current_member: Member = Depends(get_current_member)) -> Member:
    if current_member.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return current_member
