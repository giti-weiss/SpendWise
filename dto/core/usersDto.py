from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserBaseDTO(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class UserCreateDTO(UserBaseDTO):
    password_hash: str


class UserResponseDTO(UserBaseDTO):
    user_id: int
    join_date: datetime

    class Config:
        from_attributes = True