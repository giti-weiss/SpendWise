from models.core.UserCategoryGoal import UserCategoryGoal
from repositories.base_repository import BaseRepository


class UserCategoryGoalRepository(BaseRepository):

    def get_by_id(self, id):
        return (
            self.session.query(UserCategoryGoal)
            .filter_by(id=id)
            .first()
        )

    def get_all(self):
        return self.session.query(UserCategoryGoal).all()
    def get_by_user(self, user_id):
        return (
            self.session.query(UserCategoryGoal)
            .filter_by(user_id=user_id)
            .all()
        )

    def get_by_user_and_category(self, user_id, category_id):
        return (
            self.session.query(UserCategoryGoal)
            .filter_by(user_id=user_id, category_id=category_id)
            .first()
        )

    def create(self, obj_data: dict):
        obj = UserCategoryGoal(**obj_data)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def update(self, id, **kwargs):
        obj = self.get_by_id(id)
        if not obj:
            return None

        for key, value in kwargs.items():
            setattr(obj, key, value)

        self.session.commit()
        return obj

    def delete_by_id(self, id):
        obj = self.get_by_id(id)
        if obj:
            self.delete(obj)
        return obj