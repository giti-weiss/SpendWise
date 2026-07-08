from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


class UserCategoryGoalCreateDTO(BaseModel):
    user_id: int
    category_id: int
    current_price: Decimal
    target_price: Decimal


class UserCategoryGoalResponseDTO(UserCategoryGoalCreateDTO):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True