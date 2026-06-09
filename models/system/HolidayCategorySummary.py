from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from models.base import Base

class HolidayCategorySummary(Base):
    __tablename__ = "Holiday_Category_Summary"

    summary_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("Users.user_id"))
    category_id = Column(Integer, ForeignKey("Categories.category_id"))
    change_ratio = Column(Numeric(5,2))
    last_calculated = Column(DateTime)

    user = relationship("User", back_populates="holiday_summaries")
    category = relationship("Category", back_populates="holiday_summaries")