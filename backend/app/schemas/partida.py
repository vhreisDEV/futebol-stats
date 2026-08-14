from pydantic import BaseModel
from datetime import date
from typing import Optional


class PartidaDetalheResponse(BaseModel):
    id: int
    data: date
    rodada: Optional[int]
    time_mandante_id: int
    time_mandante: str
    time_visitante_id: int
    time_visitante: str
    gols_mandante: int
    gols_visitante: int
    escanteios_mandante: int
    escanteios_visitante: int
    chutes_mandante: int
    chutes_visitante: int
    chutes_gol_mandante: int
    chutes_gol_visitante: int
    cartoes_amarelos_mandante: int
    cartoes_amarelos_visitante: int
    cartoes_vermelhos_mandante: int
    cartoes_vermelhos_visitante: int
