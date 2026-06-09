from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db_connection import get_db

from dto.system.HolidayCategorySummaryDto import HolidayCategorySummaryCreateDTO
from services.system.HolidayCategorySummary import HolidayCategorySummaryService
from repositories.system.HolidayCategorySummary import HolidayCategorySummaryRepository

router = APIRouter(prefix="/holiday-summaries", tags=["Holiday Category Summary"])


def get_service(db: Session = Depends(get_db)):
    return HolidayCategorySummaryService(HolidayCategorySummaryRepository(db))


@router.get("/")
def get_all(service=Depends(get_service)):
    return service.get_all()


@router.get("/{summary_id}")
def get_by_id(summary_id: int, service=Depends(get_service)):
    result = service.get_by_id(summary_id)
    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@router.get("/user/{user_id}")
def get_by_user(user_id: int, service=Depends(get_service)):
    return service.get_by_user(user_id)


@router.get("/user/{user_id}/category/{category_id}")
def get_by_user_and_category(user_id: int, category_id: int, service=Depends(get_service)):
    result = service.get_by_user_and_category(user_id, category_id)
    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@router.post("/")
def create(dto: HolidayCategorySummaryCreateDTO, service=Depends(get_service)):
    return service.create(dto)


@router.put("/{summary_id}")
def update(summary_id: int, change_ratio, service=Depends(get_service)):
    result = service.update(summary_id, change_ratio)
    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@router.delete("/{summary_id}")
def delete(summary_id: int, service=Depends(get_service)):
    success = service.delete(summary_id)
    if not success:
        raise HTTPException(status_code=404, detail="Not found")
    return {"success": True}