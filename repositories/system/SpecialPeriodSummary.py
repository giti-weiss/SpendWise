from models.system.SpecialPeriodSummary import SpecialPeriodSummary
from models.system.SpecialDate import SpecialDate
from models.system.HolidayCategorySummary import HolidayCategorySummary


class SpecialPeriodSummaryRepository:

    def __init__(self, session):
        self.session = session

    # ================= CRUD =================

    def get_all(self):
        return self.session.query(SpecialPeriodSummary).all()

    def get_by_id(self, summary_id):
        return self.session.query(SpecialPeriodSummary).filter_by(
            summary_id=summary_id
        ).first()

    def create(self, obj):
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def update(self, obj):
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, obj):
        self.session.delete(obj)
        self.session.commit()

    # ================= BUSINESS =================

    def resolve_period(self, expense_date):

        period = self.session.query(SpecialDate).filter(
            SpecialDate.start_date <= expense_date,
            SpecialDate.end_date >= expense_date
        ).first()

        if period:
            return period

        return self.session.query(SpecialDate).filter(
            SpecialDate.start_date > expense_date
        ).order_by(SpecialDate.start_date.asc()).first()

    def get_ratio(self, period_id, category_id):

        row = self.session.query(HolidayCategorySummary).filter_by(
            special_period_id=period_id,
            category_id=category_id
        ).first()

        if not row or row.change_ratio is None:
            return 0.0

        try:
            return float(row.change_ratio)
        except (ValueError, TypeError):
            return 0.0

    def get_summary(self, user_id, category_id, period_id):

        return self.session.query(SpecialPeriodSummary).filter_by(
            user_id=user_id,
            category_id=category_id,
            special_period_id=period_id
        ).first()