from typing import List, Optional
from pydantic import BaseModel


class CampeonatoResponse(BaseModel):
    id: int
    nome: str
    pais_nome: str
    pais_codigo: str
    temporada: int
    rodadas_total: Optional[int]
    ativo: bool
    rodada_atual: Optional[int] = None
    total_times: int = 0


class ListaCampeonatosResponse(BaseModel):
    campeonatos: List[CampeonatoResponse]
