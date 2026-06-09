from typing import List, Optional
from sqlalchemy.orm import Session

from models.reporting.ReportTypes import ReportType


class ReportTypesRepository:

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, report_type_id: int) -> Optional[ReportType]:
        return (
            self.session.query(ReportType)
            .filter(ReportType.report_type_id == report_type_id)
            .first()
        )

    def get_all(self) -> List[ReportType]:
        return self.session.query(ReportType).all()

    def create(self, report_type_name: str) -> ReportType:
        obj = ReportType(report_type_name=report_type_name)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def update(self, report_type_id: int, **kwargs) -> Optional[ReportType]:
        obj = self.get_by_id(report_type_id)
        if not obj:
            return None

        for key, value in kwargs.items():
            if hasattr(obj, key):
                setattr(obj, key, value)

        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete_by_id(self, report_type_id: int) -> bool:
        obj = self.get_by_id(report_type_id)
        if not obj:
            return False

        self.session.delete(obj)
        self.session.commit()
        return True