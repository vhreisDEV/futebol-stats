from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
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
    modelo = Column(String, nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
