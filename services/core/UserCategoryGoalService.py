from typing import List, Optional, Dict

from dto.core.UserCategoryGoalDto import (
    UserCategoryGoalResponseDTO
)

from repositories.core.UserCategoryGoalRepository import UserCategoryGoalRepository


class UserCategoryGoalService:

    def __init__(self, repository: UserCategoryGoalRepository):
        self.repository = repository

    # ================= BASIC =================

    def get_all(self) -> List[UserCategoryGoalResponseDTO]:
        return [
            UserCategoryGoalResponseDTO.model_validate(x)
            for x in self.repository.get_all()
        ]

    def get_by_id(self, id: int) -> Optional[UserCategoryGoalResponseDTO]:
        obj = self.repository.get_by_id(id)
        return UserCategoryGoalResponseDTO.model_validate(obj) if obj else None

    def get_by_user(self, user_id: int) -> List[UserCategoryGoalResponseDTO]:
        return [
            UserCategoryGoalResponseDTO.model_validate(x)
            for x in self.repository.get_by_user(user_id)
        ]

    def get_targets_map(self, user_id: int) -> Dict[int, float]:
        """
        מחזיר dict: {category_id: target_amount}
        שימושי ל-CutRankingService / BudgetPlanService.
        """
        return self.repository.get_targets_map(user_id)

    # ================= CORE =================

    def recalculate_for_user(self, user_id: int) -> List[UserCategoryGoalResponseDTO]:
        """
        מחשב מחדש את כל היעדים החודשיים למשתמש לפי:
        target_amount = amount_per_person × family_size
        """
        results = self.repository.recalculate_for_user(user_id)
        return [
            UserCategoryGoalResponseDTO.model_validate(x)
            for x in results
        ]
