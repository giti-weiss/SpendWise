from typing import List, Optional

from dto.system.MonthlyExpensesSummaryDto import MonthlyExpensesSummaryDto
from repositories.system.Monthly_Expenses_Summary import MonthlyExpensesSummaryRepository


class MonthlyExpensesSummaryService:

    def __init__(self, repository: MonthlyExpensesSummaryRepository):
        self.repository = repository

    def create(self, dto: MonthlyExpensesSummaryDto):
        obj = self.repository.create({
            "user_id": dto.user_id,
            "category_id": dto.category_id,
            "category_name": dto.category_name,
            "month_year": dto.month_year,
            "total_amount": dto.total_amount,
            "created_at": dto.created_at
        })
        return obj

    def get_by_id(self, summary_id: int):
        return self.repository.get_by_id(summary_id)

    def get_all(self):
        return self.repository.get_all()

    def get_by_user(self, user_id: int):
        return self.repository.get_by_user(user_id)

    def update(self, summary_id: int, total_amount: int):
        return self.repository.update(summary_id, total_amount=total_amount)

    def delete(self, summary_id: int):
        return self.repository.delete_by_id(summary_id)