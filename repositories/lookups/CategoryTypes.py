# repositories/enums/category_types_repository.py

from models.lookups import CategogyType
from repositories.base_repository import BaseRepository


class CategoryTypesRepository(BaseRepository):

    def get_by_id(self, category_type_id):
        return (
            self.session.query(CategogyType)
            .filter_by(category_type_id=category_type_id)
            .first()
        )

    def get_all(self):
        return self.session.query(CategogyType).all()

    def update(self, category_type_id, **kwargs):
        category_type = self.get_by_id(category_type_id)

        if not category_type:
            return None

        for key, value in kwargs.items():
            setattr(category_type, key, value)

        self.session.commit()
        return category_type

    def delete_by_id(self, category_type_id):
        category_type = self.get_by_id(category_type_id)

        if category_type:
            self.delete(category_type)

        return category_type