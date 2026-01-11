import re

from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator

from extracto.utils.util import RoleEnum


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    role: str = RoleEnum.USER


    @field_validator
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        """
        Validate password strength:
        - At least 8 characters
        - At least on uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """

        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        
        if not re.search(r'[A-Z]', value):
            raise ValueError('Password must contain at least one uppercase letter.')
        
        if not re.search(r'[A-Z]', value):
            raise ValueError('Password must contain at least one lowercase letter.')
        
        if not re.search(r'\d', value):
            raise ValueError('Password must contain at least one digit letter.')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValueError('Password must contain at least one special letter.')

    @field_validator
    @classmethod
    def sanitize_name(cls, value: Optional[str]) -> Optional[str]:
        """
        Sanitize name inputs to prevent injection attacks.
        
        :param cls: Description
        :param value: Description
        :type value: Optional[str]
        :return: Description
        :rtype: str | None
        """

        value = re.sub(r'[<>\"\'`;]', '', value)
        return value.strip()[:256]


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
