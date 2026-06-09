from pydantic import BaseModel


class ReportTypeDTO(BaseModel):
    report_type_id: int
    report_type_name: str

    class Config:
        from_attributes = True