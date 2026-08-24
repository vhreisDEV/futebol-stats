from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base


class Campeonato(Base):
    """Uma liga + temporada especifica (ex.: Brasileirao Serie A 2026,
    Premier League 2026/27) -- Time e Partida pertencem a um Campeonato,
    nunca a mais de um. `id_externo_liga` e o league id da Highlightly,
    usado pelos scripts de import; `pais_codigo` segue o formato ISO que a
    Highlightly retorna (ex.: "BR", "GB-ENG"), pensado pra exibir a
    bandeira do pais na UI."""

    __tablename__ = "campeonatos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    pais_nome = Column(String, nullable=False)
    pais_codigo = Column(String, nullable=False)
    temporada = Column(Integer, nullable=False)
    id_externo_liga = Column(Integer, nullable=True, index=True)
    rodadas_total = Column(Integer, nullable=True)
    ativo = Column(Boolean, nullable=False, default=True)
