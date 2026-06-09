from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dto.reporting.ReportTypesDto import ReportTypeDTO
from services.Reports.ReportTypes import ReportTypesService
from repositories.reporting.ReportTypes import ReportTypesRepository
from db_connection import get_db


router = APIRouter(prefix="/report-types", tags=["Report Types"])


def get_service(db: Session = Depends(get_db)) -> ReportTypesService:
    repo = ReportTypesRepository(db)
    return ReportTypesService(repo)


@router.get("/", response_model=list[ReportTypeDTO])
def get_all(service: ReportTypesService = Depends(get_service)):
    return service.get_all()


@router.get("/{report_type_id}", response_model=ReportTypeDTO)
def get_by_id(report_type_id: int, service: ReportTypesService = Depends(get_service)):
    result = service.get_by_id(report_type_id)
    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@router.post("/", response_model=ReportTypeDTO)
def create(report_type_name: str, service: ReportTypesService = Depends(get_service)):
    return service.create(report_type_name)


@router.put("/{report_type_id}", response_model=ReportTypeDTO)
def update(report_type_id: int, report_type_name: str, service: ReportTypesService = Depends(get_service)):
    result = service.update(report_type_id, report_type_name)
    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@router.delete("/{report_type_id}")
def delete(report_type_id: int, service: ReportTypesService = Depends(get_service)):
    success = service.delete(report_type_id)
    if not success:
        raise HTTPException(status_code=404, detail="Not found")
    return {"success": True}