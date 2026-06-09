from dto.Finance.ExpensesDto import ExpenseCreateDTO
from repositories.Finance.Expenses import ExpenseRepository
from models.Finance.Expenses import Expense
from datetime import date

class ExpenseService:
    def __init__(self, repository: ExpenseRepository):
        self.repo = repository

    # --- CREATE ---
    def add_expense(self, dto: ExpenseCreateDTO) -> Expense:
        expense = Expense(
            user_id=dto.user_id,
            amount=dto.amount,
            date=dto.date,
            ExpenseTypes=dto.expense_type_id,
            category_id=dto.category_id
        )
        self.repo.add(expense)
        return expense

    # --- READ ALL ---
    def get_all_expenses(self):
        return self.repo.get_all()

    # --- READ BY ID ---
    def get_expense_by_id(self, expense_id: int):
        return self.repo.get_by_id(expense_id)

    # --- UPDATE ---
    def update_expense(self, expense_id: int, dto: ExpenseCreateDTO):
        return self.repo.update(
            expense_id,
            user_id=dto.user_id,
            amount=dto.amount,
            date=dto.date,
            ExpenseTypes=dto.expense_type_id,
            category_id=dto.category_id
        )

    # --- DELETE ---
    def delete_expense(self, expense_id: int):
        return self.repo.delete_by_id(expense_id)