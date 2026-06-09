from pydantic import BaseModel
from datetime import date


class IncomeFrequencyDTO(BaseModel):
    frequency_id: int
    frequency_name: str

    class Config:
        from_attributes = True


class IncomeCreateDTO(BaseModel):
    user_id: int
    frequency_id: int
    amount: int
    date: date


class IncomeResponseDTO(IncomeCreateDTO):
    transaction_id: int

    class Config:
        from_attributes = True