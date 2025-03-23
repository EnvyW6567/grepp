from sqlalchemy.orm import Session

from src.member.model import Member


class MemberRepository:
    def find_by_id(self, db: Session, member_id: int):
        return db.query(Member).filter(Member.id == member_id).first()

    def find_by_username(self, db: Session, username: str):
        return db.query(Member).filter(Member.username == username).first()

    def save(self, db: Session, member: Member):
        db.add(member)
        db.commit()
        db.refresh(member)
        return member

    def delete(self, db: Session, member: Member):
        db.delete(member)
        db.commit()

        return True
