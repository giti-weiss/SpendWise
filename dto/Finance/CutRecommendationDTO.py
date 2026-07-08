from pydantic import BaseModel


class CutRecommendationDTO(BaseModel):
    category_id: int
    category_name: str
    current_amount: float
    recommended_cut_pct: float