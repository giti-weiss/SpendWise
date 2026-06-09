# services/categories_service.py
class CategoriesService:
    def __init__(self, repo):
        self.repo = repo

    def add_category(self, dto):
        category = self.repo.model(
            category_name=dto.category_name,
            category_type_id=dto.category_type_id,
            category_description=dto.category_description,
            user_id=dto.user_id,
            created_at=dto.created_at
        )
        self.repo.add(category)

    def get_all_categories(self):
        return self.repo.get_all_categories()

    def get_category_by_id(self, category_id):
        return self.repo.get_by_id(category_id)

    def update_category(self, category_id, dto):
        return self.repo.update(category_id,
                                category_name=dto.category_name,
                                category_type_id=dto.category_type_id,
                                category_description=dto.category_description,
                                user_id=dto.user_id,
                                created_at=dto.created_at)

    def delete_category(self, category_id):
        return self.repo.delete_by_id(category_id)
def get_incomes_by_category(self, user_id):
    # סיכום הכנסות לפי קטגוריות
    incomes = self.income_repo.get_by_user(user_id)
    categories = {}
    for i in incomes:
        cat_name = self.category_repo.get_by_id(i.category_id).category_name
        categories[cat_name] = categories.get(cat_name, 0) + i.amount
    return categories

