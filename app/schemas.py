"""Shapes of data going in and out of the API (the contract with other teams).

Note: there is no password_hash here, so it can never leak in a response.
"""
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Role(str, Enum):
    student = "student"
    admin = "admin"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    token: str
    user_id: int
    role: Role


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int = Field(validation_alias="id")
    name: str
    email: EmailStr
    role: Role


class ProfileUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
