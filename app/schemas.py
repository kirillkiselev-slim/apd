from datetime import datetime

from pydantic import BaseModel


class Document(BaseModel):
    id: int
    rubrics: str
    text: str
    created_date: datetime

    class Config:
        orm_mode = True
        from_attributes = True
