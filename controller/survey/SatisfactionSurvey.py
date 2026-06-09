from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dto.survey.SatisfactionSurveyDto import (
    SatisfactionSurveyCreateDTO,
    SatisfactionSurveyResponseDTO
)
from services.survey.SatisfactionSurvey import SatisfactionSurveyService
from repositories.survey.SatisfactionSurvey import SatisfactionSurveyRepository
from db_connection import get_db


router = APIRouter(prefix="/satisfaction-survey", tags=["Satisfaction Survey"])


def get_service(db: Session = Depends(get_db)) -> SatisfactionSurveyService:
    repo = SatisfactionSurveyRepository(db)
    return SatisfactionSurveyService(repo)


@router.get("/", response_model=list[SatisfactionSurveyResponseDTO])
def get_all(service: SatisfactionSurveyService = Depends(get_service)):
    return service.get_all()


@router.get("/{survey_id}", response_model=SatisfactionSurveyResponseDTO)
def get_by_id(survey_id: int, service: SatisfactionSurveyService = Depends(get_service)):
    result = service.get_by_id(survey_id)
    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@router.get("/user/{user_id}", response_model=list[SatisfactionSurveyResponseDTO])
def get_by_user(user_id: int, service: SatisfactionSurveyService = Depends(get_service)):
    return service.get_by_user(user_id)


@router.post("/", response_model=SatisfactionSurveyResponseDTO)
def create(dto: SatisfactionSurveyCreateDTO, service: SatisfactionSurveyService = Depends(get_service)):
    return service.create(dto)


@router.put("/{survey_id}", response_model=SatisfactionSurveyResponseDTO)
def update(survey_id: int, feedback: str, service: SatisfactionSurveyService = Depends(get_service)):
    result = service.update(survey_id, feedback)
    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@router.delete("/{survey_id}")
def delete(survey_id: int, service: SatisfactionSurveyService = Depends(get_service)):
    success = service.delete(survey_id)
    if not success:
        raise HTTPException(status_code=404, detail="Not found")
    return {"success": True}