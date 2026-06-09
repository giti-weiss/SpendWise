from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db_connection import get_db
from dto.system.SpecialDateDto import SpecialDateCreateDTO
from services.system.SpecialDates import SpecialDatesService
from repositories.system.SpecialDates import SpecialDatesRepository

router = APIRouter(prefix="/special-dates", tags=["Special Dates"])


def get_service(db: Session = Depends(get_db)):
    repo = SpecialDatesRepository(db)
    return SpecialDatesService(repo)


@router.post("/")
def create(dto: SpecialDateCreateDTO, service: SpecialDatesService = Depends(get_service)):
    return service.create(dto)


@router.get("/")
def get_all(service: SpecialDatesService = Depends(get_service)):
    return service.get_all()


@router.get("/{special_date_id}")
def get_by_id(special_date_id: int, service: SpecialDatesService = Depends(get_service)):
    result = service.get_by_id(special_date_id)
    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@router.get("/user/{user_id}")
def get_by_user(user_id: int, service: SpecialDatesService = Depends(get_service)):
    return service.get_by_user(user_id)


@router.put("/{special_date_id}")
def update(special_date_id: int, service: SpecialDatesService = Depends(get_service), **kwargs):
    result = service.update(special_date_id, **kwargs)
    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@router.delete("/{special_date_id}")
def delete(special_date_id: int, service: SpecialDatesService = Depends(get_service)):
    success = service.delete(special_date_id)
    if not success:
        raise HTTPException(status_code=404, detail="Not found")
    return {"success": True}