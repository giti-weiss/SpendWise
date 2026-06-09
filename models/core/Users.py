from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from models.base import Base

class User(Base):
    __tablename__ = "Users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    join_date = Column(DateTime, nullable=False)

    categories = relationship("Category", back_populates="user")
    incomes = relationship("Income", back_populates="user")
    expenses = relationship("Expense", back_populates="user")
    goals = relationship("Goal", back_populates="user")
    satisfaction_surveys = relationship(
        "SatisfactionSurvey",
        back_populates="user"
    )
    reports = relationship("Report", back_populates="user")
    recommendations = relationship("Recommendation", back_populates="user")
    special_dates = relationship("SpecialDate", back_populates="user")
    special_expenses = relationship("SpecialExpense", back_populates="user")
    forecasts = relationship("FinancialForecast", back_populates="user")
    holiday_summaries = relationship("HolidayCategorySummary", back_populates="user")
    goal_expectations = relationship(
        "GoalExpectation",
        back_populates="user"
    )
    monthly_expense_summaries = relationship(
        "MonthlyExpensesSummary",
        back_populates="user"
    )