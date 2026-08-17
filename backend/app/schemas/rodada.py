from pydantic import BaseModel
from datetime import date
from typing import List, Optional


class PartidaRodadaResponse(BaseModel):
    id: int
    data: date
    status: str
    time_mandante_id: int
    time_mandante: str
    time_visitante_id: int
    time_visitante: str
    gols_mandante: Optional[int]
    gols_visitante: Optional[int]


class RodadaResponse(BaseModel):
    rodada: int
    partidas: List[PartidaRodadaResponse]


class RodadaAtualResponse(BaseModel):
    rodada_atual: int
    rodada_maxima: int
