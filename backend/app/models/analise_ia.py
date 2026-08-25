from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database import Base


class AnaliseIAPartida(Base):
    __tablename__ = "analises_ia_partida"

    id = Column(Integer, primary_key=True, index=True)
    # Gera uma vez so e cacheia -- cada chamada de IA tem custo, nao vale
    # regenerar toda vez que alguem abre a pagina da partida.
    partida_id = Column(Integer, ForeignKey("partidas.id"), unique=True, nullable=False, index=True)
    texto = Column(String, nullable=False)
    # Paragrafo curto sintetizando os mercados de "totais do jogo"
    # (chutes/escanteios/cartoes somando os dois times) -- nulo pras
    # linhas geradas antes dessa coluna existir.
    dicas = Column(String, nullable=True)
    # Cache dos destaques/bilhetes ja calculados (JSON), pra nao recalcular
    # do zero (varias queries) toda vez que alguem abre a pagina -- so
    # invalida quando um dos dois times joga uma partida nova (ver
    # mandante_ultimo_jogo/visitante_ultimo_jogo). Nulo pras linhas geradas
    # antes dessa coluna existir (cai de volta pro recalculo).
    destaques_json = Column(Text, nullable=True)
    mandante_ultimo_jogo = Column(Date, nullable=True)
    visitante_ultimo_jogo = Column(Date, nullable=True)
    modelo = Column(String, nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
