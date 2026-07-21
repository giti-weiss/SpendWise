from models.system.SpecialPeriodSummary import SpecialPeriodSummary
from models.system.SpecialDate import SpecialDate


class SpecialPeriodService:
    """
    Handles individual expenses recorded during special periods (holidays).
    If a category has a change_ratio in Holiday_Category_Summary for
    the active period, applies a discount to the expense amount.
    """

    def __init__(self, repo):
        self.repo = repo

    # ==================================================================
    # API for GradualBudgetService — resolve period + ratios
    # ==================================================================
    def resolve_period_ratios(self, year, month):
        """
        Returns (period, ratios_dict) for a given year/month.
        Uses resolve_period which returns:
        - The holiday overlapping the month, OR
        - The next upcoming holiday (user may prepare early)
        - period: SpecialDate row (or None)
        - ratios_dict: {category_id: change_ratio} (0–1 range)
        """
        from datetime import date as dt, timedelta

        first_day = dt(year, month, 1)
        if month == 12:
            last_day = dt(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = dt(year, month + 1, 1) - timedelta(days=1)

        # Try first day, then last day of month
        period = self.repo.resolve_period(first_day) or self.repo.resolve_period(last_day)
        if not period:
            return None, {}

        ratios = self.repo.get_ratios_by_period(period.type_id)
        return period, ratios

    # ==================================================================
    # Original API — expense adjustment
    # ==================================================================
    def handle_expense(self, user_id, category_id, amount, expense_date):
        """
        Returns adjusted amount for an expense during a special period.
        - If no active period → returns original amount
        - If category NOT in Holiday_Category_Summary for this period → returns original amount
        - If category IS in the table → applies (1 - ratio) discount
        - If spending already exceeded approved amount → applies 5% penalty reduction
        """
        # 1. find active period for this date
        period = self.repo.resolve_period(expense_date)
        if not period:
            return amount  # no holiday → unchanged

        # 2. check if this category has a ratio for this period
        ratio = self.repo.get_ratio(period.type_id, category_id)
        if ratio <= 0:
            return amount  # category not in holiday → unchanged

        # normalize ratio to 0–1
        if ratio > 1:
            ratio = ratio / 100
        ratio = max(0, min(ratio, 1))

        # 3. check if spending has exceeded the approved budget
        summary = self.repo.get_summary(user_id, category_id, period.type_id)

        if summary and summary.approved_amount > 0 and summary.spent_amount >= summary.approved_amount:
            # exceeded — apply 5% penalty
            return amount * 0.95

        # 4. apply holiday discount
        final_price = amount * (1 - ratio)

        # 5. track spending
        if not summary:
            summary = SpecialPeriodSummary(
                user_id=user_id,
                category_id=category_id,
                special_period_id=period.type_id,
                spent_amount=0,
                approved_amount=0
            )
            self.repo.create(summary)

        summary.spent_amount += final_price
        summary.approved_amount += amount * ratio

        self.repo.update(summary)

        return final_price
