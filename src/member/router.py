from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.db.db import get_db
from src.member.schema import MemberResponse, MemberCreate, MemberUpdate
from src.member.service import MemberService

router = APIRouter(
    prefix="/members",
    tags=["members"],
    responses={404: {"description": "Not found"}},
)

member_service = MemberService()


@router.post("/", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(member: MemberCreate, db: Session = Depends(get_db)) -> MemberResponse:
    member = member_service.create(db=db, member_create=member)

    if member is None:
        raise HTTPException(status_code=400, detail="Username already registered")

    return member


@router.put("/{member_id}", response_model=MemberResponse)
def update_member(member_id: int, member: MemberUpdate, db: Session = Depends(get_db)) -> MemberResponse:
    member = member_service.update(db, member_id=member_id, member_update=member)

    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")

    return member


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(member_id: int, db: Session = Depends(get_db)) -> None:
    success = member_service.delete(db, member_id=member_id)
    if not success:
        raise HTTPException(status_code=404, detail="Member not found")

    return None
