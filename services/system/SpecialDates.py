from dto.system.SpecialDateDto import SpecialDateCreateDTO, SpecialDateResponseDTO
from repositories.system.SpecialDates import SpecialDatesRepository


class SpecialDatesService:

    def __init__(self, repository: SpecialDatesRepository):
        self.repository = repository

    def create(self, dto: SpecialDateCreateDTO):
        obj = self.repository.create(dto.dict())
        return SpecialDateResponseDTO.model_validate(obj)

    def get_by_id(self, special_date_id: int):
        obj = self.repository.get_by_id(special_date_id)
        return SpecialDateResponseDTO.model_validate(obj) if obj else None

    def get_all(self):
        return [
            SpecialDateResponseDTO.model_validate(x)
            for x in self.repository.get_all()
        ]

    def get_by_user(self, user_id: int):
        return [
            SpecialDateResponseDTO.model_validate(x)
            for x in self.repository.get_by_user(user_id)
        ]

    def update(self, special_date_id: int, **kwargs):
        obj = self.repository.update(special_date_id, **kwargs)
        return SpecialDateResponseDTO.model_validate(obj) if obj else None

    def delete(self, special_date_id: int):
        return self.repository.delete_by_id(special_date_id)