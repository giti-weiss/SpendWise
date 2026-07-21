from flask import Blueprint, jsonify, request
from datetime import date
from db_connection import SessionLocal

from services.Finance.budget_service import BudgetService
from services.Finance.EarlyWarningService import EarlyWarningService
from services.system.MonthlyExpensesSummary import MonthlyExpensesSummaryService
from services.system.SpecialPeriodSummary import SpecialPeriodService
from services.Finance.GradualBudgetService import GradualBudgetService
from services.Finance.CategoryBehaviorService import CategoryBehaviorService
from services.Finance.BehaviorStressService import BehaviorStressService
from services.Finance.HolidayAdjustmentService import HolidayAdjustmentService
from services.Finance.FinancialHealthService import FinancialHealthService
from services.Finance.FinancialStressService import FinancialStressService

from repositories.Finance.BudgetRepository import BudgetRepository
from repositories.core.UserCategoryPreferenceRepository import UserCategoryPreferenceRepository
from repositories.core.CategoryStandard import CategoryStandardRepository
from repositories.system.MonthlyExpensesSummary import MonthlyExpensesSummaryRepository
from repositories.system.EarlyWarningAlert import EarlyWarningAlertRepository
from repositories.Finance.BudgetPlanRepository import BudgetPlanRepository
from repositories.system.SpecialPeriodSummary import SpecialPeriodSummaryRepository
from repositories.core.UserCategoryGoalRepository import UserCategoryGoalRepository
from repositories.Finance.FinancialRepository import FinancialRepository

budget_plan_controller = Blueprint("budget_plan", __name__)


def _build_service(session):
    budget_repo = BudgetRepository(session)
    preference_repo = UserCategoryPreferenceRepository(session)
    standard_repo = CategoryStandardRepository(session)
    monthly_repo = MonthlyExpensesSummaryRepository(session)
    plan_repo = BudgetPlanRepository(session)
    alert_repo = EarlyWarningAlertRepository(session)
    special_period_repo = SpecialPeriodSummaryRepository(session)
    user_goal_repo = UserCategoryGoalRepository(session)
    financial_repo = FinancialRepository(session)

    budget_service = BudgetService(budget_repo)
    special_period_service = SpecialPeriodService(special_period_repo)
    analysis_service = MonthlyExpensesSummaryService(monthly_repo, special_period_service)
    behavior_stress = BehaviorStressService(monthly_repo, analysis_service)
    category_behavior = CategoryBehaviorService()
    holiday_adjustment = HolidayAdjustmentService(session)
    early_warning = EarlyWarningService(session, alert_repo)
    spike_service = FinancialStressService(financial_repo, analysis_service)
    financial_health = FinancialHealthService(spike_service, behavior_stress, financial_repo)

    gradual = GradualBudgetService(
        session=session,
        budget_service=budget_service,
        monthly_analysis_service=analysis_service,
        behavior_stress_service=behavior_stress,
        category_behavior_service=category_behavior,
        holiday_adjustment_service=holiday_adjustment,
        special_period_service=special_period_service,
        budget_plan_repository=plan_repo,
        user_goal_repo=user_goal_repo,
        preference_repo=preference_repo,
        standard_repo=standard_repo,
    )
    return gradual, plan_repo, early_warning, financial_health


# ── build plan ──

@budget_plan_controller.route("/budget/plan/<int:user_id>/<int:year>/<int:month>", methods=["GET"])
def get_budget_plan_route(user_id, year, month):
    session = SessionLocal()
    try:
        svc, _, _, _ = _build_service(session)
        result = svc.build_plan(user_id, year, month)
        return jsonify(result), 200
    except Exception as ex:
        session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(ex)}), 500
    finally:
        session.close()


# ── budget status ──

@budget_plan_controller.route("/budget/status", methods=["GET"])
def get_budget_status():
    """GET /budget/status?user_id=1&year=2026&month=7"""
    user_id = request.args.get("user_id", type=int)
    today = date.today()
    year = request.args.get("year", today.year, type=int)
    month = request.args.get("month", today.month, type=int)

    session = SessionLocal()
    try:
        _, plan_repo, early_warning_service, _ = _build_service(session)

        rows = plan_repo.get_plan_for_month(user_id, year, month)
        plan_dict = {
            "budget": [
                {"category_id": r.category_id, "category_name": r.category.name if r.category else None,
                 "planned_amount": r.planned_amount}
                for r in rows
            ],
            "monthly_limit": sum(r.planned_amount for r in rows),
        }

        warning_result = early_warning_service.check_spending_vs_budget(
            user_id, year, month, plan_dict
        )

        rebalance = early_warning_service.suggest_rebalance(
            user_id, year, month, plan_dict
        )

        return jsonify({
            "year": year,
            "month": month,
            "monthly_limit": plan_dict["monthly_limit"],
            "status": warning_result,
            "rebalance": rebalance,
        }), 200
    except Exception as ex:
        session.rollback()
        return jsonify({"success": False, "message": str(ex)}), 500
    finally:
        session.close()


# ── view raw Budget_Plans data ──

@budget_plan_controller.route("/budget/plans", methods=["GET"])
def get_budget_plans_data():
    """GET /budget/plans?user_id=1&year=2026&month=7"""
    user_id = request.args.get("user_id", type=int)
    today = date.today()
    year = request.args.get("year", today.year, type=int)
    month = request.args.get("month", today.month, type=int)

    session = SessionLocal()
    try:
        _, plan_repo, _, _ = _build_service(session)
        rows = plan_repo.get_plan_for_month(user_id, year, month)
        return jsonify({
            "year": year,
            "month": month,
            "plans": [
                {
                    "user_id": r.user_id,
                    "category_id": r.category_id,
                    "planned_amount": r.planned_amount,
                    "holiday_adjustment": r.holiday_adjustment,
                    "holiday_name": r.holiday_name,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in rows
            ]
        }), 200
    except Exception as ex:
        session.rollback()
        return jsonify({"success": False, "message": str(ex)}), 500
    finally:
        session.close()


# ── apply rebalance transfers ──

# ── program status ──

@budget_plan_controller.route("/budget/program/<int:user_id>", methods=["GET"])
def get_program_status(user_id):
    """GET /budget/program/<user_id> — מצב התוכנית"""
    session = SessionLocal()
    try:
        svc, _, _, _ = _build_service(session)
        phase_info = svc._get_program_phase_info(user_id)
        phase_info["months_active"] = svc._count_program_months(user_id)
        return jsonify(phase_info), 200
    except Exception as ex:
        session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(ex)}), 500
    finally:
        session.close()


# ── program summary (before/after report) ──

@budget_plan_controller.route("/budget/program/<int:user_id>/summary", methods=["GET"])
def get_program_summary(user_id):
    """GET /budget/program/<user_id>/summary — דו&quot;ח סיכום תוכנית"""
    session = SessionLocal()
    try:
        svc, _, _, _ = _build_service(session)
        summary = svc.generate_program_summary(user_id)
        if "error" in summary:
            return jsonify({"success": False, "message": summary["error"]}), 404
        return jsonify(summary), 200
    except Exception as ex:
        session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(ex)}), 500
    finally:
        session.close()


# ── financial health score ──

@budget_plan_controller.route("/budget/health/<int:user_id>", methods=["GET"])
def get_financial_health(user_id):
    """
    GET /budget/health/<user_id>?year=2025&month=8
    Returns the user's current financial stress level at any time.
    Simple, always available, no arguments required (defaults to current month).
    """
    from datetime import date as dt

    today = dt.today()
    year = request.args.get("year", today.year, type=int)
    month = request.args.get("month", today.month, type=int)

    session = SessionLocal()
    try:
        _, _, _, financial_health = _build_service(session)

        result = financial_health.calculate_financial_score(user_id, year, month)
        metrics = financial_health.get_metrics(user_id, year, month)
        explanation = financial_health.build_smart_explanation_v2(metrics)

        return jsonify({
            "user_id": user_id,
            "year": year,
            "month": month,
            "score": result["ציון"],
            "status": result["status"],
            "explanation": explanation,
            "details": {
                "spike_stress": metrics["spike"],
                "behavior_stress": metrics["behavior"],
                "budget_pressure": metrics["budget"],
            },
        }), 200
    except Exception as ex:
        session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(ex)}), 500
    finally:
        session.close()


# ── end-of-month dashboard ──

@budget_plan_controller.route("/budget/dashboard/<int:user_id>/<int:year>/<int:month>", methods=["GET"])
def get_monthly_dashboard(user_id, year, month):
    """
    GET /budget/dashboard/<user_id>/<year>/<month>
    Returns a complete organized dashboard for end-of-month review.
    """
    from datetime import date
    from repositories.core.UserSavingGoalRepository import UserSavingGoalRepository
    from repositories.core.SavingsGoalRepository import SavingsGoalRepository
    from services.core.UserSavingGoalService import UserSavingGoalService
    from services.core.SavingsGoalService import SavingsGoalService

    session = SessionLocal()
    try:
        svc, plan_repo, ew_service, financial_health = _build_service(session)

        # 1. Budget plan for next month
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1
        plan = svc.build_plan(user_id=user_id, year=next_year, month=next_month)

        # 2. Current month status (spending vs budget)
        current_rows = plan_repo.get_plan_for_month(user_id, year, month)
        spending_status = None
        if current_rows:
            pdict = {
                "budget": [
                    {"category_id": r.category_id,
                     "category_name": r.category.category_name if r.category else f"cat{r.category_id}",
                     "planned_amount": r.planned_amount}
                    for r in current_rows
                ],
                "monthly_limit": sum(r.planned_amount for r in current_rows),
            }
            try:
                spending_status = ew_service.check_spending_vs_budget(user_id, year, month, pdict)
            except Exception:
                spending_status = None

        # 3. Savings
        saving_goal_repo = UserSavingGoalRepository(session)
        savings_repo = SavingsGoalRepository(session)
        saving_service = UserSavingGoalService(saving_goal_repo)
        savings_service = SavingsGoalService(savings_repo)

        goals = savings_service.get_by_user(user_id)
        allocations = saving_service.get_monthly_allocations(user_id, year, month)
        savings_balance = sum(g.current_balance for g in goals)

        # 4. Program phase
        phase = svc._get_program_phase_info(user_id)

        # 5. Active alerts
        active_alerts = ew_service.get_active_alerts(user_id, year, month)

        # 6. Holiday info
        holiday = plan.get("holiday")

        # ---- BUILD ORGANIZED RESPONSE ----
        return jsonify({
            "date": f"{year}-{month:02d}",
            "program": {
                "phase": phase["phase"],
                "month": phase["program_month"],
                "remaining": phase["remaining_months"],
            },

            "current_month": {
                "year": year,
                "month": month,
                "spending_status": spending_status["status"] if spending_status else "N/A",
                "total_spent": spending_status["general"]["total_spent"] if spending_status else 0,
                "monthly_limit": spending_status["general"]["monthly_limit"] if spending_status else 0,
                "alerts": [
                    {"type": a.alert_type, "severity": a.severity, "title": a.title}
                    for a in active_alerts[:10]
                ],
            },

            "next_month_budget": {
                "year": next_year,
                "month": next_month,
                "mode": plan["mode"],
                "net_budget": plan["net_budget"],
                "planned_spending": plan["planned_spending"],
                "projected_savings": plan["saved_this_month"],
                "status": plan["status"],
                "categories": [
                    {
                        "category_id": b["category_id"],
                        "category_name": b["category_name"],
                        "current_spending": b["current_amount"],
                        "target": b["target_amount"],
                        "planned": b["planned_amount"],
                        "reduction": b["reduction"],
                        "reduction_percent": b["reduction_pct"],
                        "status": b["status"],
                        "is_essential": b["is_essential"],
                        "is_fixed_cost": b["is_fixed_cost"],
                    }
                    for b in plan["budget"]
                ],
                "holiday": {
                    "active": holiday is not None,
                    "name": holiday["name"] if holiday else None,
                    "start": holiday["start_date"] if holiday else None,
                    "end": holiday["end_date"] if holiday else None,
                    "affected_categories": len(holiday["ratios"]) if holiday else 0,
                } if holiday else None,
            },

            # 7. Financial health — always available snapshot
            "financial_health": (
                lambda fh: {
                    "score": fh["ציון"],
                    "status": fh["status"],
                    "explanation": financial_health.build_smart_explanation_v2(
                        financial_health.get_metrics(user_id, year, month)
                    ),
                    "details": {
                        "spike_stress": fh.get("spike_stress", 0),
                        "behavior_stress": fh.get("behavior_stress", 0),
                        "budget_pressure": fh.get("budget_pressure", 0),
                    },
                }
            )(financial_health.calculate_financial_score(user_id, year, month)),

            "savings": {
                "available_for_savings": plan["saved_this_month"],
                "total_saved_so_far": round(savings_balance, 2),
                "goals": [
                    {
                        "id": g.id,
                        "name": g.name,
                        "balance": g.current_balance,
                        "target": g.target_amount,
                        "allocated_this_month": next(
                            (a.allocated_amount for a in allocations if a.goal_id == g.id), 0
                        ),
                    }
                    for g in goals
                ],
            },

            "warnings": plan.get("warnings") or [],
        }), 200

    except Exception as ex:
        session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(ex)}), 500
    finally:
        session.close()


# ── apply rebalance transfers ──

@budget_plan_controller.route("/budget/rebalance/apply", methods=["POST"])
def apply_rebalance():
    session = SessionLocal()
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        year = data.get("year")
        month = data.get("month")
        transfers = data.get("transfers", [])

        _, plan_repo, early_warning_service, _ = _build_service(session)
        result = early_warning_service.apply_rebalance(
            user_id, year, month, transfers, plan_repo
        )
        return jsonify(result), 200
    except Exception as ex:
        session.rollback()
        return jsonify({"success": False, "message": str(ex)}), 500
    finally:
        session.close()
