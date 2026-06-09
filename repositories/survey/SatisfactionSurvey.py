from typing import List, Optional

from models.survey.SatisfactionSurvey import SatisfactionSurvey
from repositories.base_repository import BaseRepository


class SatisfactionSurveyRepository(BaseRepository):

    def get_by_id(self, survey_id: int) -> Optional[SatisfactionSurvey]:
        return (
            self.session.query(SatisfactionSurvey)
            .filter_by(survey_id=survey_id)
            .first()
        )

    def get_all(self) -> List[SatisfactionSurvey]:
        return self.session.query(SatisfactionSurvey).all()

    def get_by_user(self, user_id: int) -> List[SatisfactionSurvey]:
        return (
            self.session.query(SatisfactionSurvey)
            .filter_by(user_id=user_id)
            .all()
        )

    def create(self, user_id: int, survey_date, feedback: str = None) -> SatisfactionSurvey:
        obj = SatisfactionSurvey(
            user_id=user_id,
            survey_date=survey_date,
            feedback=feedback
        )
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def update(self, survey_id: int, **kwargs) -> Optional[SatisfactionSurvey]:
        obj = self.get_by_id(survey_id)
        if not obj:
            return None

        for key, value in kwargs.items():
            if hasattr(obj, key):
                setattr(obj, key, value)

        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete_by_id(self, survey_id: int) -> bool:
        obj = self.get_by_id(survey_id)
        if not obj:
            return False

        self.session.delete(obj)
        self.session.commit()
        return True