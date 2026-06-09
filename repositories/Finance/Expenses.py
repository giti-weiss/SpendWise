# repositories/expense_repository.py
from models.Finance.Expenses import Expense
from repositories.base_repository import BaseRepository


class ExpenseRepository(BaseRepository):

    def get_by_id(self, expense_id):
        return (
            self.session.query(Expense)
            .filter_by(ExpenseId=expense_id)
            .first()
        )

    def get_all(self):
        return self.session.query(Expense).all()

    def exists_by_name(self, name):
        return (
            self.session.query(Expense)
            .filter_by(ExpenseName=name)
            .first() is not None
        )

    def update(self, expense_id, **kwargs):
        expense = self.get_by_id(expense_id)

        if not expense:
            return None

        for key, value in kwargs.items():
            setattr(expense, key, value)

        self.session.commit()
        return expense

    def delete_by_id(self, expense_id):
        expense = self.get_by_id(expense_id)

        if expense:
            self.delete(expense)

        return expense