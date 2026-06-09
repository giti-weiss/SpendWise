from flask import Blueprint, request, jsonify
from dto.Finance.ExpenseTypeDto import ExpenseTypeDTO
from services.Finance.ExpenseTypes import ExpenseTypeService
from repositories.Finance.ExpenseTypes import ExpenseTypesRepository
from db_connection import SessionLocal

# יצירת סשן
session = SessionLocal()
repo = ExpenseTypesRepository(session)
service = ExpenseTypeService(repo)

expense_types_blueprint = Blueprint('expense_types', __name__)

@expense_types_blueprint.route('', methods=['POST'])
def add_expense_type():
    dto = ExpenseTypeDTO(**request.get_json())
    expense_type = service.add_expense_type(dto)
    return jsonify({"ExpenseTypeId": expense_type.expenseTypeId}), 201

@expense_types_blueprint.route('', methods=['GET'])
def get_expense_types():
    types = service.get_all_expense_types()
    return jsonify([{"ExpenseTypeId": t.expenseTypeId, "ExpenseTypeName": t.expenseTypeName} for t in types])

@expense_types_blueprint.route('/<int:type_id>', methods=['GET'])
def get_expense_type(type_id):
    expense_type = service.get_expense_type_by_id(type_id)
    if not expense_type:
        return jsonify({"error": "Expense type not found"}), 404
    return jsonify({"ExpenseTypeId": expense_type.expenseTypeId, "ExpenseTypeName": expense_type.expenseTypeName})

@expense_types_blueprint.route('/<int:type_id>', methods=['PUT'])
def update_expense_type(type_id):
    dto = ExpenseTypeDTO(**request.get_json())
    expense_type = service.update_expense_type(type_id, dto)
    if not expense_type:
        return jsonify({"error": "Expense type not found"}), 404
    return jsonify({"message": "Expense type updated"})

@expense_types_blueprint.route('/<int:type_id>', methods=['DELETE'])
def delete_expense_type(type_id):
    expense_type = service.delete_expense_type(type_id)
    if not expense_type:
        return jsonify({"error": "Expense type not found"}), 404
    return jsonify({"message": "Expense type deleted"})