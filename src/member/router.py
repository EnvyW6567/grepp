from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.auth.dependencies import get_current_member
from src.db.db import get_db
from src.member.model import Member
from src.member.schema import MemberResponse, MemberCreate, MemberUpdate, LoginResponse
from src.member.service import MemberService

router = APIRouter(
    prefix="/members",
    tags=["members"],
    responses={404: {"description": "Not found"}},
)

member_service = MemberService()


@router.post("/", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def create(member_create: MemberCreate, db: Session = Depends(get_db)) -> MemberResponse:
    member = member_service.create(db, member_create)

    if member is None:
        raise HTTPException(status_code=400, detail="Username already registered")

    return member


@router.put("/", response_model=MemberResponse)
def update(member_update: MemberUpdate,
           db: Session = Depends(get_db),
           member: Member = Depends(get_current_member), ) -> MemberResponse:
    member_update = member_service.update(db, member, member_update=member_update)

    if member_update is None:
        raise HTTPException(status_code=404, detail="Member not found")

    return member_update


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(member_id: int, db: Session = Depends(get_db)) -> None:
    success = member_service.delete(db, member_id=member_id)
    if not success:
        raise HTTPException(status_code=404, detail="Member not found")

    return None


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
def login(member_login: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> LoginResponse:
    loginResponse = member_service.login(db, member_login)

    if loginResponse is None:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    return loginResponse
