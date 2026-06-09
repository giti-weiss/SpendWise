from models.system.SpecialDate import SpecialDate
from repositories.base_repository import BaseRepository


class SpecialDatesRepository(BaseRepository):

    def create(self, obj_data: dict):
        obj = SpecialDate(**obj_data)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def get_by_id(self, special_date_id: int):
        return (
            self.session.query(SpecialDate)
            .filter_by(special_date_id=special_date_id)
            .first()
        )

    def get_all(self):
        return self.session.query(SpecialDate).all()

    def get_by_user(self, user_id: int):
        return (
            self.session.query(SpecialDate)
            .filter_by(user_id=user_id)
            .all()
        )

    def update(self, special_date_id: int, **kwargs):
        obj = self.get_by_id(special_date_id)

        if not obj:
            return None

        for key, value in kwargs.items():
            setattr(obj, key, value)

        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete_by_id(self, special_date_id: int):
        obj = self.get_by_id(special_date_id)

        if obj:
            self.session.delete(obj)
            self.session.commit()
            return True

        return False