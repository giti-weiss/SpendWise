from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from models.base import Base
class SpecialDate(Base):
    __tablename__ = "Special_Dates"

    special_date_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("Users.user_id"))
    type_id = Column(Integer, ForeignKey("Special_Date_Types.type_id"))
    date = Column(Date)

    user = relationship("User", back_populates="special_dates")
