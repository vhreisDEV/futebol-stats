from pydantic import BaseModel
from datetime import date, time
from typing import Optional


class PartidaDetalheResponse(BaseModel):
    id: int
    data: Optional[date]
    hora: Optional[time]
    status: str
    rodada: Optional[int]
    time_mandante_id: int
    time_mandante: str
    time_visitante_id: int
    time_visitante: str
    gols_mandante: Optional[int]
    gols_visitante: Optional[int]
    escanteios_mandante: Optional[int]
    escanteios_visitante: Optional[int]
    chutes_mandante: Optional[int]
    chutes_visitante: Optional[int]
    chutes_gol_mandante: Optional[int]
    chutes_gol_visitante: Optional[int]
    cartoes_amarelos_mandante: Optional[int]
    cartoes_amarelos_visitante: Optional[int]
    cartoes_vermelhos_mandante: Optional[int]
    cartoes_vermelhos_visitante: Optional[int]
