from pydantic import BaseModel
from datetime import date

class FinancialForecastsDto(BaseModel):
    forecast_id: int
    user_id: int
    category_id: int
    forecast_date: date
    count: int
    range_id: int