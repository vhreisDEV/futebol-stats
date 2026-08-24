from typing import List, Optional
from pydantic import BaseModel

from app.schemas.destaque import Destaque


class MelhorMercado(BaseModel):
    time: str  # "mandante" ou "visitante"
    nome_time: str
    destaque: Destaque


class AnaliseIAResponse(BaseModel):
    partida_id: int
    disponivel: bool
    texto: Optional[str] = None
    gerado_em: Optional[str] = None
    destaques_mandante: List[Destaque] = []
    destaques_visitante: List[Destaque] = []
    melhor_mercado: Optional[MelhorMercado] = None
