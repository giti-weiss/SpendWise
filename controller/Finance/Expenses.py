from flask import Blueprint, request, jsonify
from dto.Finance.ExpensesDto import ExpenseCreateDTO, ExpenseResponseDTO
from services.Finance.Expenses import ExpenseService
from repositories.Finance.Expenses import ExpenseRepository
from db_connection import SessionLocal

# יצירת סשן
session = SessionLocal()
repo = ExpenseRepository(session)
service = ExpenseService(repo)

expenses_blueprint = Blueprint('expenses', __name__)

@expenses_blueprint.route('', methods=['POST'])
def add_expense():
    dto = ExpenseCreateDTO(**request.get_json())
    expense = service.add_expense(dto)
    return jsonify({"transaction_id": expense.transaction_id}), 201

@expenses_blueprint.route('', methods=['GET'])
def get_expenses():
    expenses = service.get_all_expenses()
    return jsonify([ExpenseResponseDTO.from_orm(e).dict() for e in expenses])

@expenses_blueprint.route('/<int:expense_id>', methods=['GET'])
def get_expense(expense_id):
    expense = service.get_expense_by_id(expense_id)
    if not expense:
        return jsonify({"error": "Expense not found"}), 404
    return jsonify(ExpenseResponseDTO.from_orm(expense).dict())

@expenses_blueprint.route('/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    dto = ExpenseCreateDTO(**request.get_json())
    expense = service.update_expense(expense_id, dto)
    if not expense:
        return jsonify({"error": "Expense not found"}), 404
    return jsonify({"message": "Expense updated"})

@expenses_blueprint.route('/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    expense = service.delete_expense(expense_id)
    if not expense:
        return jsonify({"error": "Expense not found"}), 404
    return jsonify({"message": "Expense deleted"})