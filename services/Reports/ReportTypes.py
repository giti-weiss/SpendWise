from typing import List, Optional

from dto.reporting.ReportTypesDto import ReportTypeDTO
from repositories.reporting.ReportTypes import ReportTypesRepository


class ReportTypesService:

    def __init__(self, repository: ReportTypesRepository):
        self.repository = repository

    def get_by_id(self, report_type_id: int) -> Optional[ReportTypeDTO]:
        obj = self.repository.get_by_id(report_type_id)
        return ReportTypeDTO.model_validate(obj) if obj else None

    def get_all(self) -> List[ReportTypeDTO]:
        return [
            ReportTypeDTO.model_validate(x)
            for x in self.repository.get_all()
        ]

    def create(self, report_type_name: str) -> ReportTypeDTO:
        obj = self.repository.create(report_type_name)
        return ReportTypeDTO.model_validate(obj)

    def update(self, report_type_id: int, report_type_name: str) -> Optional[ReportTypeDTO]:
        obj = self.repository.update(report_type_id, report_type_name=report_type_name)
        return ReportTypeDTO.model_validate(obj) if obj else None

    def delete(self, report_type_id: int) -> bool:
        return self.repository.delete_by_id(report_type_id)