class UserSavingGoalService:
    """
    ניהול הקצאת חיסכון חודשית.

    זרימה:
    1. תחילת חודש — job יוצר רשומות ריקות לכל יעדי החיסכון
    2. המשתמש נכנס, רואה את הסכום הפנוי, ממלא כמה רוצה לכל יעד
    3. המשתמש מאשר — הסכומים מועברים ל-Savings_Goals (current_balance) + Transactions
    """

    def __init__(self, repo):
        self.repo = repo

    def get_monthly_allocations(self, user_id, year, month):
        """מחזיר את ההקצאות של החודש."""
        return self.repo.get_for_month(user_id, year, month)

    def create_initial_for_month(self, user_id, year, month, goals):
        """יוצר רשומות התחלתיות (0₪) בתחילת חודש."""
        return self.repo.create_initial_for_month(user_id, year, month, goals)

    def update_allocations(self, user_id, year, month, allocations):
        """המשתמש מעדכן סכומים."""
        return self.repo.update_allocation(user_id, year, month, allocations)

    def apply_savings(self, user_id, year, month, savings_goal_service):
        """
        מחיל את ההקצאות — מעביר כסף ל-Savings_Goals.
        נקרא כשהמשתמש מאשר את ההקצאה.

        מחזיר: list of {"goal_id": X, "goal_name": Y, "added": Z, "new_balance": W}
        """
        pending = self.repo.get_pending_allocations(user_id, year, month)
        results = []

        for record in pending:
            if record.allocated_amount > 0:
                txn = savings_goal_service.deposit(
                    goal_id=record.goal_id,
                    amount=record.allocated_amount,
                    description=f"הקצאה חודשית — {year}-{month:02d}"
                )
                self.repo.mark_applied(record)
                results.append({
                    "goal_id": record.goal_id,
                    "goal_name": record.goal.name if record.goal else "",
                    "added": record.allocated_amount,
                    "new_balance": record.goal.current_balance if record.goal else 0,
                })

        return results
