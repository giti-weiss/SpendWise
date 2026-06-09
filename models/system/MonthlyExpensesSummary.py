import datetime

from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import relationship
from models.base import Base


class MonthlyExpensesSummary(Base):
    __tablename__ = "Monthly_Expenses_Summary"

    summary_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("Users.user_id"), nullable=False)
    category_id = Column(Integer, ForeignKey("Categories.category_id"), nullable=False)

    category_name = Column(String(100), nullable=False)
    month_year = Column(String(7), nullable=False)  # YYYY-MM
    total_amount = Column(Integer, nullable=False)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship(
        "User",
        back_populates="monthly_expense_summaries"
    )

    category = relationship(
        "Category",
        back_populates="monthly_expense_summaries"
    )