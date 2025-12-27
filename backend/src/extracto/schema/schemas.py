# auth/schemas.py
from typing import Optional

from pydantic import BaseModel, EmailStr

from extracto.utils.util import RoleEnum


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    firstName: Optional[str]
    lastName: Optional[str]
    role: str = RoleEnum.USER


class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str]
    is_active: bool
    is_verified: bool

    class Config:
        orm_mode = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginSchema(BaseModel):
    email: EmailStr
    password: str
