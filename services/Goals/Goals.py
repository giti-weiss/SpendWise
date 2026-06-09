# services/goals_service.py
from dto.Goals.GoalsDto import GoalCreateDTO, GoalDetailCreateDTO
from repositories.Goals.Goals import GoalsRepository
from repositories.Goals.Goals import GoalDetailsRepository
from models.Goals.Goals import Goal
from models.Goals.GoalDetails import GoalDetail


class GoalsService:
    def __init__(self, goals_repo: GoalsRepository, details_repo: GoalDetailsRepository):
        self.goals_repo = goals_repo
        self.details_repo = details_repo

    # Goals
    def create_goal(self, dto: GoalCreateDTO):
        goal = Goal(
            user_id=dto.user_id,
            goal_created_date=dto.goal_created_date
        )
        self.goals_repo.add(goal)
        return goal

    def get_all_goals(self):
        return self.goals_repo.get_all()

    def get_goal_by_id(self, goal_id: int):
        return self.goals_repo.get_by_id(goal_id)

    def update_goal(self, goal_id: int, dto: GoalCreateDTO):
        return self.goals_repo.update(
            goal_id,
            user_id=dto.user_id,
            goal_created_date=dto.goal_created_date
        )

    def delete_goal(self, goal_id: int):
        return self.goals_repo.delete_by_id(goal_id)

    # GoalDetails
    def create_goal_detail(self, dto: GoalDetailCreateDTO):
        detail = GoalDetail(
            goal_id=dto.goal_id,
            goal_type_id=dto.goal_type_id,
            goal_description=dto.goal_description,
            goal_target_date=dto.goal_target_date,
            status_id=dto.status_id
        )
        self.details_repo.add(detail)
        return detail

    def get_goal_details(self, goal_id: int):
        return self.details_repo.get_by_goal(goal_id)

    def update_goal_detail(self, detail_id: int, dto: GoalDetailCreateDTO):
        return self.details_repo.update(
            detail_id,
            goal_id=dto.goal_id,
            goal_type_id=dto.goal_type_id,
            goal_description=dto.goal_description,
            goal_target_date=dto.goal_target_date,
            status_id=dto.status_id
        )

    def delete_goal_detail(self, detail_id: int):
        return self.details_repo.delete_by_id(detail_id)