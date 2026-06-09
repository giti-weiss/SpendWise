from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db_connection import get_db
from dto.system.MonthlyExpensesSummaryDto import MonthlyExpensesSummaryDto
from services.system.Monthly_Expenses_Summary import MonthlyExpensesSummaryService
from repositories.system.Monthly_Expenses_Summary import MonthlyExpensesSummaryRepository

router = APIRouter(prefix="/monthly-expenses-summary", tags=["Monthly Expenses Summary"])


def get_service(db: Session = Depends(get_db)):
    repo = MonthlyExpensesSummaryRepository(db)
    return MonthlyExpensesSummaryService(repo)


@router.post("/")
def create(dto: MonthlyExpensesSummaryDto, service: MonthlyExpensesSummaryService = Depends(get_service)):
    return service.create(dto)


@router.get("/")
def get_all(service: MonthlyExpensesSummaryService = Depends(get_service)):
    return service.get_all()


@router.get("/{summary_id}")
def get_by_id(summary_id: int, service: MonthlyExpensesSummaryService = Depends(get_service)):
    result = service.get_by_id(summary_id)
    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@router.get("/user/{user_id}")
def get_by_user(user_id: int, service: MonthlyExpensesSummaryService = Depends(get_service)):
    return service.get_by_user(user_id)


@router.put("/{summary_id}")
def update(summary_id: int, total_amount: int, service: MonthlyExpensesSummaryService = Depends(get_service)):
    result = service.update(summary_id, total_amount)
    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@router.delete("/{summary_id}")
def delete(summary_id: int, service: MonthlyExpensesSummaryService = Depends(get_service)):
    success = service.delete(summary_id)
    if not success:
        raise HTTPException(status_code=404, detail="Not found")
    return {"success": True}