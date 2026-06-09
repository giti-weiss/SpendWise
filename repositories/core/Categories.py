# repositories/categories_repository.py
from models.core.Categories import Category
from repositories.base_repository import BaseRepository

class CategoriesRepository(BaseRepository):
    def get_by_id(self, category_id):
        return self.session.query(Category).filter_by(category_id=category_id).first()

    def get_all_categories(self):
        return self.session.query(Category).all()

    def update(self, category_id, **kwargs):
        item = self.get_by_id(category_id)
        if not item:
            return None
        for key, value in kwargs.items():
            setattr(item, key, value)
        self.session.commit()
        return item

    def delete_by_id(self, category_id):
        item = self.get_by_id(category_id)
        if item:
            self.delete(item)
        return item
