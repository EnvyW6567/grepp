import hashlib
import os

from sqlalchemy.orm import Session

from src.member.model import Member, Role
from src.member.repository import MemberRepository
from src.member.schema import MemberCreate, MemberUpdate, MemberResponse


class MemberService:
    def __init__(self):
        self.repository = MemberRepository()

    def _hash_password(self, password: str) -> str:
        salt = os.urandom(32)
        pw_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return salt.hex() + ':' + pw_hash.hex()

    def _get_by_id(self, db: Session, member_id: int) -> MemberResponse:
        member = self.repository.find_by_id(db, member_id)
        if not member:
            return None
        return MemberResponse.model_validate(member)

    def _get_by_username(self, db: Session, username: str) -> Member:
        return self.repository.find_by_username(db, username)

    def create(self, db: Session, member_create: MemberCreate) -> MemberResponse:
        existing_member = self.repository.find_by_username(db, username=member_create.username)
        if existing_member:
            return None

        hashed_password = self._hash_password(member_create.password)

        member = Member(
            username=member_create.username,
            password=hashed_password,
            role=Role.USER
        )

        saved_member = self.repository.save(db, member)
        return MemberResponse.model_validate(saved_member)

    def update(self, db: Session, member_id: int, member_update: MemberUpdate) -> MemberResponse:
        member = self.repository.find_by_id(db, member_id)
        if not member:
            return None

        update_data = member_update.dict(exclude_unset=True)

        if 'password' in update_data:
            update_data['password'] = self._hash_password(update_data['password'])

        for key, value in update_data.items():
            setattr(member, key, value)

        updated_member = self.repository.save(db, member)
        
        return MemberResponse.model_validate(updated_member)

    def delete(self, db: Session, member_id: int) -> bool:
        member = self.repository.find_by_id(db, member_id)
        if not member:
            return False

        return self.repository.delete(db, member)
