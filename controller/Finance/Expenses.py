from flask import Blueprint, request, jsonify
from dto.Finance.ExpensesDto import ExpenseCreateDTO, ExpenseResponseDTO
from services.Finance.Expenses import ExpenseService
from repositories.Finance.Expenses import ExpenseRepository
from services.Finance.EarlyWarningService import EarlyWarningService
from repositories.system.EarlyWarningAlert import EarlyWarningAlertRepository
from db_connection import SessionLocal

expenses_blueprint = Blueprint('expenses', __name__, url_prefix='/expenses')


def get_service():
    session = SessionLocal()
    repo = ExpenseRepository(session)
    service = ExpenseService(repo)
    alert_repo = EarlyWarningAlertRepository(session)
    early_warning = EarlyWarningService(session, alert_repo)
    return session, service, early_warning


# ==================== יצירת הוצאה (POST) ====================
@expenses_blueprint.route('/', methods=['POST'])
def add_expense():
    session, service, ew_service = get_service()
    try:
        dto = ExpenseCreateDTO(**request.get_json())

        # Step 0: Smart alert check BEFORE saving
        alert_result = ew_service.check_before_expense(
            user_id=dto.user_id,
            year=dto.date.year,
            month=dto.date.month,
            amount=dto.amount,
            category_id=dto.category_id,
            category_name="",  # Will be resolved from DB later if needed
        )

        # Step 1: Save the expense
        expense = service.add_expense(dto)

        return jsonify({
            "transaction_id": expense.transaction_id,
            "alerts": alert_result,
        }), 201
    finally:
        session.close()


# ==================== בדיקת חריגה לפני הוצאה (POST) ====================
@expenses_blueprint.route('/check', methods=['POST'])
def check_before_expense():
    """
    Check if an expense will exceed budget BEFORE the user confirms.
    Body: {user_id, amount, category_id, year, month, category_name}
    """
    session, _, ew_service = get_service()
    try:
        data = request.get_json()
        result = ew_service.check_before_expense(
            user_id=data["user_id"],
            year=data["year"],
            month=data["month"],
            amount=data["amount"],
            category_id=data["category_id"],
            category_name=data.get("category_name", ""),
        )
        return jsonify(result), 200
    finally:
        session.close()


# ==================== קבלת כל ההוצאות (GET) ====================
@expenses_blueprint.route('/', methods=['GET'])
def get_expenses():
    session, service, _ = get_service()
    try:
        expenses = service.get_all_expenses()
        return jsonify([ExpenseResponseDTO.from_orm(e).dict() for e in expenses])
    finally:
        session.close()


# ==================== קבלת הוצאה לפי ID (GET) ====================
@expenses_blueprint.route('/<int:expense_id>', methods=['GET'])
def get_expense(expense_id):
    session, service, _ = get_service()
    try:
        expense = service.get_expense_by_id(expense_id)
        if not expense:
            return jsonify({"error": "Expense not found"}), 404
        return jsonify(ExpenseResponseDTO.from_orm(expense).dict())
    finally:
        session.close()


# ==================== עדכון הוצאה (PUT) ====================
@expenses_blueprint.route('/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    session, service, _ = get_service()
    try:
        dto = ExpenseCreateDTO(**request.get_json())
        expense = service.update_expense(expense_id, dto)
        if not expense:
            return jsonify({"error": "Expense not found"}), 404
        return jsonify({"message": "Expense updated"})
    finally:
        session.close()


# ==================== מחיקת הוצאה (DELETE) ====================
@expenses_blueprint.route('/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    session, service, _ = get_service()
    try:
        expense = service.delete_expense(expense_id)
        if not expense:
            return jsonify({"error": "Expense not found"}), 404
        return jsonify({"message": "Expense deleted"})
    finally:
        session.close()

