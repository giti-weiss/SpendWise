from pydantic import BaseModel
from datetime import datetime

class MonthlyExpensesSummaryDto(BaseModel):
    summary_id: int
    user_id: int
    category_id: int
    category_name: str
    month_year: str
    total_amount: int
    created_at: datetime