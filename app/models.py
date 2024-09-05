from sqlalchemy import Column, Integer, String, Text, DateTime

from app.database import Base


class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, index=True)
    rubrics = Column(String)
    text = Column(Text, nullable=False)
    created_date = Column(DateTime, nullable=False)
