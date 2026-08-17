from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class EstatisticaJogadorPartida(Base):
    __tablename__ = "estatisticas_jogador_partida"

    id = Column(Integer, primary_key=True, index=True)
    jogador_id = Column(Integer, ForeignKey("jogadores.id"), nullable=False, index=True)
    partida_id = Column(Integer, ForeignKey("partidas.id"), nullable=False, index=True)
    time_id = Column(Integer, ForeignKey("times.id"), nullable=False)

    minutos_jogados = Column(Integer, nullable=True)

    gols = Column(Integer, nullable=False, default=0)
    assistencias = Column(Integer, nullable=False, default=0)
    cartoes_amarelos = Column(Integer, nullable=False, default=0)
    cartoes_vermelhos = Column(Integer, nullable=False, default=0)

    # Sem default: nem toda fonte de dados fornece esses campos por jogador,
    # e default=0 faria um dado ausente parecer "zero" de verdade (mesmo bug
    # ja corrigido nos campos 1T/2T de Partida -- ver corrigir_1t_2t_nulos.py).
    chutes = Column(Integer, nullable=True)
    chutes_gol = Column(Integer, nullable=True)
    desarmes = Column(Integer, nullable=True)
    faltas_cometidas = Column(Integer, nullable=True)
    faltas_sofridas = Column(Integer, nullable=True)
    defesas = Column(Integer, nullable=True)  # so se aplica a goleiros

    jogador = relationship("Jogador", foreign_keys=[jogador_id])
    partida = relationship("Partida", foreign_keys=[partida_id])
    time = relationship("Time", foreign_keys=[time_id])
