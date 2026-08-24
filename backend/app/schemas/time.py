from pydantic import BaseModel
from datetime import date
from typing import List, Optional


class TimeBase(BaseModel):
    id: int
    nome: str

    class Config:
        from_attributes = True


class TimeDetalheResponse(TimeBase):
    campeonato_id: Optional[int]


class JogoResponse(BaseModel):
    id: int
    # Nulo quando so temos o placar (ex.: veio do PDF da CBF, sem data
    # oficial nem estatisticas granulares da Highlightly ainda).
    data: Optional[date]
    adversario: str
    casa_ou_fora: str
    resultado: str
    gols_time: int
    gols_adversario: int
    escanteios_time: Optional[int]
    escanteios_adversario: Optional[int]
    escanteios_1t_time: Optional[int]
    escanteios_1t_adversario: Optional[int]
    escanteios_2t_time: Optional[int]
    escanteios_2t_adversario: Optional[int]
    chutes_time: Optional[int]
    chutes_adversario: Optional[int]
    chutes_1t_time: Optional[int]
    chutes_1t_adversario: Optional[int]
    chutes_gol_time: Optional[int]
    chutes_gol_adversario: Optional[int]
    cartoes_amarelos_time: Optional[int]
    cartoes_amarelos_adversario: Optional[int]
    cartoes_vermelhos_time: Optional[int]
    cartoes_vermelhos_adversario: Optional[int]


class EstatisticasResponse(BaseModel):
    total_jogos: int
    vitorias: int
    empates: int
    derrotas: int
    gols_marcados: int
    gols_sofridos: int
    media_gols: float
    media_escanteios: float
    media_chutes: float
    media_chutes_gol: float
    media_cartoes_amarelos: float
    media_cartoes_vermelhos: float
    sequencia_recente: List[str]