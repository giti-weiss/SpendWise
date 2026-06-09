from pydantic import BaseModel


class ExpenseTypeDTO(BaseModel):
    ExpenseTypeId: int
    ExpenseTypeName: str

    class Config:
        from_attributes = True