from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dto.survey.SurveyAnswersDto import (
    SurveyAnswerCreateDTO,
    SurveyAnswerResponseDTO
)
from services.survey.SurveyAnswers import SurveyAnswersService
from repositories.survey.SurveyAnswers import SurveyAnswersRepository
from db_connection import get_db

router = APIRouter(prefix="/survey-answers", tags=["Survey Answers"])


def get_service(db: Session = Depends(get_db)) -> SurveyAnswersService:
    repo = SurveyAnswersRepository(db)
    return SurveyAnswersService(repo)


@router.get("/", response_model=list[SurveyAnswerResponseDTO])
def get_all(service: SurveyAnswersService = Depends(get_service)):
    return service.get_all()


@router.get("/{answer_id}", response_model=SurveyAnswerResponseDTO)
def get_by_id(answer_id: int, service: SurveyAnswersService = Depends(get_service)):
    result = service.get_by_id(answer_id)
    if not result:
        raise HTTPException(status_code=404, detail="Answer not found")
    return result


@router.get("/survey/{survey_id}", response_model=list[SurveyAnswerResponseDTO])
def get_by_survey(survey_id: int, service: SurveyAnswersService = Depends(get_service)):
    return service.get_by_survey(survey_id)


@router.post("/", response_model=SurveyAnswerResponseDTO)
def create(dto: SurveyAnswerCreateDTO, service: SurveyAnswersService = Depends(get_service)):
    return service.create(dto)


@router.put("/{answer_id}", response_model=SurveyAnswerResponseDTO)
def update(answer_id: int, answer_value: int, service: SurveyAnswersService = Depends(get_service)):
    result = service.update(answer_id, answer_value)
    if not result:
        raise HTTPException(status_code=404, detail="Answer not found")
    return result


@router.delete("/{answer_id}")
def delete(answer_id: int, service: SurveyAnswersService = Depends(get_service)):
    success = service.delete(answer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Answer not found")
    return {"success": True}