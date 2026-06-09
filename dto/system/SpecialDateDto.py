from pydantic import BaseModel
from datetime import date


class SpecialDateTypeDTO(BaseModel):
    type_id: int
    type_name: str

    class Config:
        from_attributes = True


class SpecialDateCreateDTO(BaseModel):
    user_id: int
    type_id: int
    date: date


class SpecialDateResponseDTO(SpecialDateCreateDTO):
    special_date_id: int

    class Config:
        from_attributes = True