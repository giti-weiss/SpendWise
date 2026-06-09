from pydantic import BaseModel
from datetime import datetime, date


class GoalStatusDTO(BaseModel):
    status_id: int
    status_name: str

    class Config:
        from_attributes = True


class GoalCreateDTO(BaseModel):
    user_id: int
    goal_created_date: datetime


class GoalResponseDTO(GoalCreateDTO):
    goal_id: int

    class Config:
        from_attributes = True


class GoalDetailCreateDTO(BaseModel):
    goal_id: int
    goal_type_id: int
    goal_description: str
    goal_target_date: date
    status_id: int


class GoalDetailResponseDTO(GoalDetailCreateDTO):
    detail_id: int

    class Config:
        from_attributes = True