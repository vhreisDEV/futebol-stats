from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database import Base

# "agendada": data definida, ainda nao jogada. "adiada": tinha data marcada
# e foi remarcada/adiada pela CBF, nova data pode ser desconhecida.
# "finalizada": jogo aconteceu, placar e estatisticas sao reais.
STATUS_PARTIDA_PADRAO = "finalizada"


class Partida(Base):
    __tablename__ = "partidas"

    id = Column(Integer, primary_key=True, index=True)
    id_externo = Column(Integer, unique=True, nullable=True, index=True)
    time_mandante_id = Column(Integer, ForeignKey("times.id"), nullable=False)
    time_visitante_id = Column(Integer, ForeignKey("times.id"), nullable=False)
    status = Column(String, nullable=False, default=STATUS_PARTIDA_PADRAO)
    # Nula quando so temos o confronto da rodada (mandante x visitante) mas
    # ainda nao a data/hora oficial da CBF para esse jogo.
    data = Column(Date, nullable=True)
    rodada = Column(Integer, nullable=True)

    # Nulos ate a partida ser finalizada (agendada/adiada nao tem placar
    # nem estatisticas ainda). Sem default=0 -- ver nota em
    # EstatisticaJogadorPartida sobre por que isso importa.
    gols_mandante = Column(Integer, nullable=True)
    gols_visitante = Column(Integer, nullable=True)

    escanteios_mandante = Column(Integer, nullable=True)
    escanteios_visitante = Column(Integer, nullable=True)
    escanteios_1t_mandante = Column(Integer, nullable=True)
    escanteios_1t_visitante = Column(Integer, nullable=True)
    escanteios_2t_mandante = Column(Integer, nullable=True)
    escanteios_2t_visitante = Column(Integer, nullable=True)

    chutes_mandante = Column(Integer, nullable=True)
    chutes_visitante = Column(Integer, nullable=True)
    chutes_1t_mandante = Column(Integer, nullable=True)
    chutes_1t_visitante = Column(Integer, nullable=True)
    chutes_gol_mandante = Column(Integer, nullable=True)
    chutes_gol_visitante = Column(Integer, nullable=True)

    cartoes_amarelos_mandante = Column(Integer, nullable=True)
    cartoes_amarelos_visitante = Column(Integer, nullable=True)
    cartoes_vermelhos_mandante = Column(Integer, nullable=True)
    cartoes_vermelhos_visitante = Column(Integer, nullable=True)

    time_mandante = relationship("Time", foreign_keys=[time_mandante_id])
    time_visitante = relationship("Time", foreign_keys=[time_visitante_id])