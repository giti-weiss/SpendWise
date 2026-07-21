from datetime import date
from flask import Blueprint, request, jsonify
from db_connection import SessionLocal

from services.core.UserSavingGoalService import UserSavingGoalService
from services.core.SavingsGoalService import SavingsGoalService
from repositories.core.UserSavingGoalRepository import UserSavingGoalRepository
from repositories.core.SavingsGoalRepository import SavingsGoalRepository

savings_distribution_blueprint = Blueprint("savings_distribution", __name__, url_prefix="/savings/distribution")


def get_services():
    session = SessionLocal()
    saving_goal_repo = UserSavingGoalRepository(session)
    savings_repo = SavingsGoalRepository(session)
    saving_service = UserSavingGoalService(saving_goal_repo)
    savings_service = SavingsGoalService(savings_repo)
    return session, saving_service, savings_service


# =====================================================
# GET  — צפייה בהקצאות החודש
# =====================================================
@savings_distribution_blueprint.route("/<int:user_id>/<int:year>/<int:month>", methods=["GET"])
def get_allocations(user_id, year, month):
    """
    מחזיר:
    - saved_this_month: כמה כסף פנוי לחיסכון
    - allocations: ההקצאות לכל יעד
    - savings_goals: מצב כל יעדי החיסכון (יתרות)
    """
    session, saving_service, savings_service = get_services()
    try:
        allocations = saving_service.get_monthly_allocations(user_id, year, month)
        goals = savings_service.get_by_user(user_id)

        total_allocated = sum(a.allocated_amount for a in allocations)

        return jsonify({
            "user_id": user_id,
            "year": year,
            "month": month,
            "allocations": [
                {
                    "id": a.id,
                    "goal_id": a.goal_id,
                    "goal_name": a.goal.name if a.goal else "",
                    "allocated_amount": a.allocated_amount,
                    "applied": bool(a.applied),
                }
                for a in allocations
            ],
            "total_allocated": total_allocated,
            "savings_goals": [
                {
                    "id": g.id,
                    "name": g.name,
                    "current_balance": g.current_balance,
                    "target_amount": g.target_amount,
                }
                for g in goals
            ],
            "total_savings": sum(g.current_balance for g in goals),
        }), 200
    finally:
        session.close()


# =====================================================
# PUT  — עדכון הקצאות
# =====================================================
@savings_distribution_blueprint.route("/<int:user_id>/<int:year>/<int:month>", methods=["PUT"])
def update_allocations(user_id, year, month):
    """
    המשתמש ממלא סכומים לכל יעד.
    Body: {"allocations": [{"goal_id": 1, "amount": 1000}, ...]}
    """
    session, saving_service, _ = get_services()
    try:
        data = request.get_json()
        allocations = data.get("allocations", [])

        result = saving_service.update_allocations(user_id, year, month, allocations)

        return jsonify({
            "user_id": user_id,
            "year": year,
            "month": month,
            "allocations": [
                {
                    "id": r.id,
                    "goal_id": r.goal_id,
                    "allocated_amount": r.allocated_amount,
                }
                for r in result
            ],
        }), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


# =====================================================
# POST — אישור והעברה ל-Savings_Goals
# =====================================================
@savings_distribution_blueprint.route("/<int:user_id>/<int:year>/<int:month>/apply", methods=["POST"])
def apply_allocations(user_id, year, month):
    """
    מאשר את ההקצאות — מעביר כסף ל-Savings_Goals.
    """
    session, saving_service, savings_service = get_services()
    try:
        results = saving_service.apply_savings(user_id, year, month, savings_service)

        return jsonify({
            "user_id": user_id,
            "year": year,
            "month": month,
            "applied": results,
            "count": len(results),
        }), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()
