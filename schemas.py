from pydantic import BaseModel
from typing import Optional, Any

class StandardResponse(BaseModel):
    code: int
    status: str
    message: str
    data: Optional[Any] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True
