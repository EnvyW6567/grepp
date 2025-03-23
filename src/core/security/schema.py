from pydantic import BaseModel


class TokenData(BaseModel):
    id: int
    username: str
    role: str
