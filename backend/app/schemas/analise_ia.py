from typing import Optional
from pydantic import BaseModel


class NotasPartida(BaseModel):
    equilibrio: Optional[float] = None
    poder_ofensivo_mandante: Optional[float] = None
    poder_ofensivo_visitante: Optional[float] = None
    intensidade: Optional[float] = None
    confianca: Optional[float] = None


class AnaliseIAResponse(BaseModel):
    partida_id: int
    disponivel: bool
    texto: Optional[str] = None
    gerado_em: Optional[str] = None
    notas: Optional[NotasPartida] = None
