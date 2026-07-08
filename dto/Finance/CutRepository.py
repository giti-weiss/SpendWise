from models.Finance.Expenses import Expense


class CutRepository:

    def __init__(self, session):
        self.session = session

    def get_monthly_expenses(self, user_id, year, month):
        return (
            self.session.query(Expense)
            .filter_by(
                user_id=user_id,
                year=year,
                month=month
            )
            .all()
        )