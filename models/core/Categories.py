from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from models.base import Base

class Category(Base):
    __tablename__ = 'Categories'
    category_id = Column(Integer, primary_key=True)
    category_name = Column(String(100), nullable=False)
    category_type_id = Column(Integer, ForeignKey('Category_Types.category_type_id'), nullable=False)
    category_description = Column(Text)
    user_id = Column(Integer, ForeignKey('Users.user_id'), nullable=False)
    created_at = Column(DateTime, nullable=False)

    category_type = relationship("CategoryType", back_populates="categories")
    user = relationship("User", back_populates="categories")
    expenses = relationship("Expense", back_populates="category")
    special_expenses = relationship("SpecialExpense", back_populates="category")
    forecasts = relationship("FinancialForecast", back_populates="category")
    holiday_summaries = relationship("HolidayCategorySummary", back_populates="category")
    monthly_expense_summaries = relationship(
        "MonthlyExpensesSummary",
        back_populates="category"
    )