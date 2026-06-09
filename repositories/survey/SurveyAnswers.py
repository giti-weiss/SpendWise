from typing import List, Optional
from models.survey.SurveyAnswers import SurveyAnswer
from repositories.base_repository import BaseRepository


class SurveyAnswersRepository(BaseRepository):

    def get_by_id(self, answer_id: int) -> Optional[SurveyAnswer]:
        return (
            self.session.query(SurveyAnswer)
            .filter_by(answer_id=answer_id)
            .first()
        )

    def get_all(self) -> List[SurveyAnswer]:
        return self.session.query(SurveyAnswer).all()

    def get_by_survey(self, survey_id: int) -> List[SurveyAnswer]:
        return (
            self.session.query(SurveyAnswer)
            .filter_by(survey_id=survey_id)
            .all()
        )

    def create(self, survey_id, question_code, question_text, answer_value):
        obj = SurveyAnswer(
            survey_id=survey_id,
            question_code=question_code,
            question_text=question_text,
            answer_value=answer_value
        )
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def update(self, answer_id: int, **kwargs):
        obj = self.get_by_id(answer_id)
        if not obj:
            return None

        for key, value in kwargs.items():
            if hasattr(obj, key):
                setattr(obj, key, value)

        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete_by_id(self, answer_id: int) -> bool:
        obj = self.get_by_id(answer_id)
        if not obj:
            return False

        self.session.delete(obj)
        self.session.commit()
        return True