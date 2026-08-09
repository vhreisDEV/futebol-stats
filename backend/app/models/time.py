from sqlalchemy import Column, Integer, String
from app.database import Base

class Time(Base):
    __tablename__ = "times"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, index=True, nullable=False)