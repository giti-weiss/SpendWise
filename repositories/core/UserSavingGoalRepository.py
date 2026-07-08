from models.core.UserSavingGoal import UserSavingGoal
from repositories.base_repository import BaseRepository


class UserSavingGoalRepository(BaseRepository):

    def upsert(self, dto):

        goal = (
            self.session.query(UserSavingGoal)
            .filter_by(user_id=dto.user_id)
            .first()
        )

        if goal:
            goal.saving_mode = dto.saving_mode
            goal.target_percent = dto.target_percent
            goal.target_amount = dto.target_amount
        else:
            goal = UserSavingGoal(
                user_id=dto.user_id,
                saving_mode=dto.saving_mode,
                target_percent=dto.target_percent,
                target_amount=dto.target_amount
            )
            self.session.add(goal)

        self.session.commit()
        self.session.refresh(goal)
        return goal

    def get_by_user(self, user_id):

        return (
            self.session.query(UserSavingGoal)
            .filter_by(user_id=user_id)
            .first()
        )

    def get_goal_by_user(self, user_id):
        return (
            self.session.query(UserSavingGoal)
            .filter_by(user_id=user_id)
            .first()
        )