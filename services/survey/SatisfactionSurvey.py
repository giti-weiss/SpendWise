from typing import List, Optional

from dto.survey.SatisfactionSurveyDto import (
    SatisfactionSurveyCreateDTO,SatisfactionSurveyResponseDTO
)
from repositories.survey.SatisfactionSurvey import SatisfactionSurveyRepository


class SatisfactionSurveyService:

    def __init__(self, repository: SatisfactionSurveyRepository):
        self.repository = repository

    def get_by_id(self, survey_id: int) -> Optional[SatisfactionSurveyResponseDTO]:
        obj = self.repository.get_by_id(survey_id)
        return SatisfactionSurveyResponseDTO.model_validate(obj) if obj else None

    def get_all(self) -> List[SatisfactionSurveyResponseDTO]:
        return [
            SatisfactionSurveyResponseDTO.model_validate(x)
            for x in self.repository.get_all()
        ]

    def get_by_user(self, user_id: int) -> List[SatisfactionSurveyResponseDTO]:
        return [
            SatisfactionSurveyResponseDTO.model_validate(x)
            for x in self.repository.get_by_user(user_id)
        ]

    def create(self, dto: SatisfactionSurveyCreateDTO) -> SatisfactionSurveyResponseDTO:
        obj = self.repository.create(
            user_id=dto.user_id,
            survey_date=dto.survey_date,
            feedback=dto.feedback
        )
        return SatisfactionSurveyResponseDTO.model_validate(obj)

    def update(self, survey_id: int, feedback: str) -> Optional[SatisfactionSurveyResponseDTO]:
        obj = self.repository.update(survey_id, feedback=feedback)
        return SatisfactionSurveyResponseDTO.model_validate(obj) if obj else None

    def delete(self, survey_id: int) -> bool:
        return self.repository.delete_by_id(survey_id)