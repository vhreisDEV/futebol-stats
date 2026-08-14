from pydantic import BaseModel
from datetime import date
from typing import List


class PartidaRodadaResponse(BaseModel):
    id: int
    data: date
    time_mandante: str
    time_visitante: str
    gols_mandante: int
    gols_visitante: int


class RodadaResponse(BaseModel):
    rodada: int
    partidas: List[PartidaRodadaResponse]


class RodadaAtualResponse(BaseModel):
    rodada_atual: int
    rodada_maxima: int
