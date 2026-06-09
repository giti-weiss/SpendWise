# ReportTypes.py - models
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from models.base import Base

class ReportType(Base):
    __tablename__ = 'Report_Types'
    report_type_id = Column(Integer, primary_key=True)
    report_type_name = Column(String(50), unique=True, nullable=False)

    reports = relationship("Report", back_populates="report_type")