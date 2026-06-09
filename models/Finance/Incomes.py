from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from models.base import Base

class Income(Base):
    __tablename__ = 'Incomes'
    transaction_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('Users.user_id'), nullable=False)
    frequency_id = Column(Integer, ForeignKey('Income_Frequency.frequency_id'), nullable=False)
    amount = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)

    user = relationship("User", back_populates="incomes")
    frequency = relationship("IncomeFrequency", back_populates="incomes")