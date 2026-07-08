from datetime import date
from apscheduler.schedulers.background import BackgroundScheduler

from db_connection import SessionLocal

from repositories.core.Users import UserRepository
from repositories.Finance.BudgetPlanRepository import BudgetPlanRepository
from repositories.Finance.BudgetRepository import BudgetRepository
from repositories.core.UserCategoryPreferenceRepository import UserCategoryPreferenceRepository
from repositories.core.CategoryStandard import CategoryStandardRepository
from repositories.core.UserSavingGoalRepository import UserSavingGoalRepository
from repositories.system.MonthlyExpensesSummary import MonthlyExpensesSummaryRepository
from repositories.system.EarlyWarningAlert import EarlyWarningAlertRepository

from services.Finance.BudgetPlanService import BudgetPlanService
from services.Finance.budget_service import BudgetService
from services.Finance.CutRankingService import CutRankingService
from services.Finance.CutAllocationService import CutAllocationService
from services.Finance.BudgetBuilderService import BudgetBuilderService
from services.system.RecommendationTextService import RecommendationTextService
from services.Finance.EarlyWarningService import EarlyWarningService
from services.system.MonthlyExpensesSummary import MonthlyExpensesSummaryService


session = SessionLocal()


# repositories

user_repo = UserRepository(session)

budget_repo = BudgetRepository(session)

preference_repo = UserCategoryPreferenceRepository(session)

standard_repo = CategoryStandardRepository(session)

saving_repo = UserSavingGoalRepository(session)

monthly_repo = MonthlyExpensesSummaryRepository(session)

alert_repo = EarlyWarningAlertRepository(session)

plan_repo = BudgetPlanRepository(session)



# services

budget_service = BudgetService(
    budget_repo
)


monthly_service = MonthlyExpensesSummaryService(
    monthly_repo
)


ranking_service = CutRankingService(
    budget_service=budget_service,
    preference_repo=preference_repo,
    standard_repo=standard_repo,
    analysis_service=monthly_service
)


allocation_service = CutAllocationService(
    budget_service=budget_service,
    saving_repo=saving_repo,
    standard_repo=standard_repo
)


builder_service = BudgetBuilderService()

recommendation_service = RecommendationTextService()


early_warning_service = EarlyWarningService(
    session=session,
    alert_repo=alert_repo
)



budget_plan_service = BudgetPlanService(
    budget_service=budget_service,
    cut_ranking_service=ranking_service,
    cut_allocation_service=allocation_service,
    builder_service=builder_service,
    recommendation_service=recommendation_service,
    early_warning_service=early_warning_service,
    budget_plan_repository=plan_repo
)



def generate_monthly_budgets():

    session = None

    try:
        print("MONTHLY BUDGET JOB STARTED")

        session = SessionLocal()

        user_repo = UserRepository(session)

        today = date.today()

        target_year = today.year
        target_month = today.month

        users = user_repo.get_all()

        for user in users:

            try:
                budget_plan_service.build_plan(
                    user_id=user.user_id,
                    year=target_year,
                    month=target_month
                )

                print(
                    f"Created budget for user {user.user_id} "
                    f"{target_year}-{target_month}"
                )

            except Exception as e:
                print(
                    f"ERROR creating budget for user {user.user_id}: {e}"
                )

    except Exception as e:
        print(f"MONTHLY BUDGET JOB FAILED: {e}")

    finally:
        if session:
            session.close()
            print("DATABASE SESSION CLOSED")


scheduler = BackgroundScheduler()

scheduler.add_job(
    func=generate_monthly_budgets,
    trigger="interval",
    seconds=30
)

# לייצור אמיתי בתחילת חודש:
# scheduler.add_job(
#     func=generate_monthly_budgets,
#     trigger="cron",
#     day=1,
#     hour=0,
#     minute=5
# )

scheduler.start()
print("MONTHLY BUDGET SCHEDULER STARTED")