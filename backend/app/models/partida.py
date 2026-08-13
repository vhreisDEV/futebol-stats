from sqlalchemy import Column, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database import Base


class Partida(Base):
    __tablename__ = "partidas"

    id = Column(Integer, primary_key=True, index=True)
    time_mandante_id = Column(Integer, ForeignKey("times.id"), nullable=False)
    time_visitante_id = Column(Integer, ForeignKey("times.id"), nullable=False)
    gols_mandante = Column(Integer, nullable=False)
    gols_visitante = Column(Integer, nullable=False)
    data = Column(Date, nullable=False)

    escanteios_mandante = Column(Integer, nullable=False, default=0)
    escanteios_visitante = Column(Integer, nullable=False, default=0)
    escanteios_1t_mandante = Column(Integer, nullable=False, default=0)
    escanteios_1t_visitante = Column(Integer, nullable=False, default=0)
    escanteios_2t_mandante = Column(Integer, nullable=False, default=0)
    escanteios_2t_visitante = Column(Integer, nullable=False, default=0)

    chutes_mandante = Column(Integer, nullable=False, default=0)
    chutes_visitante = Column(Integer, nullable=False, default=0)
    chutes_1t_mandante = Column(Integer, nullable=False, default=0)
    chutes_1t_visitante = Column(Integer, nullable=False, default=0)
    chutes_gol_mandante = Column(Integer, nullable=False, default=0)
    chutes_gol_visitante = Column(Integer, nullable=False, default=0)

    cartoes_amarelos_mandante = Column(Integer, nullable=False, default=0)
    cartoes_amarelos_visitante = Column(Integer, nullable=False, default=0)
    cartoes_vermelhos_mandante = Column(Integer, nullable=False, default=0)
    cartoes_vermelhos_visitante = Column(Integer, nullable=False, default=0)

    time_mandante = relationship("Time", foreign_keys=[time_mandante_id])
    time_visitante = relationship("Time", foreign_keys=[time_visitante_id])