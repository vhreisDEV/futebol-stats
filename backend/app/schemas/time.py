from pydantic import BaseModel
from datetime import date
from typing import List, Optional


class TimeBase(BaseModel):
    id: int
    nome: str

    class Config:
        from_attributes = True


class JogoResponse(BaseModel):
    id: int
    data: date
    adversario: str
    casa_ou_fora: str
    resultado: str
    gols_time: int
    gols_adversario: int
    escanteios_time: int
    escanteios_adversario: int
    escanteios_1t_time: Optional[int]
    escanteios_1t_adversario: Optional[int]
    escanteios_2t_time: Optional[int]
    escanteios_2t_adversario: Optional[int]
    chutes_time: int
    chutes_adversario: int
    chutes_1t_time: Optional[int]
    chutes_1t_adversario: Optional[int]
    chutes_gol_time: int
    chutes_gol_adversario: int
    cartoes_amarelos_time: int
    cartoes_amarelos_adversario: int
    cartoes_vermelhos_time: int
    cartoes_vermelhos_adversario: int


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