from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Jogador(Base):
    __tablename__ = "jogadores"

    id = Column(Integer, primary_key=True, index=True)
    id_externo = Column(Integer, unique=True, nullable=True, index=True)
    nome = Column(String, nullable=False, index=True)
    posicao = Column(String, nullable=True)
    time_id = Column(Integer, ForeignKey("times.id"), nullable=True)

    time = relationship("Time", foreign_keys=[time_id])
