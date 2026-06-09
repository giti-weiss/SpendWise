from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CategoryBaseDTO(BaseModel):
    category_name: str
    category_type_id: int
    category_description: Optional[str] = None


class CategoryCreateDTO(CategoryBaseDTO):
    user_id: int


class CategoryResponseDTO(CategoryBaseDTO):
    category_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True