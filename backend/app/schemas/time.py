from pydantic import BaseModel
from datetime import date
from typing import List


class TimeBase(BaseModel):
    id: int
    nome: str

    class Config:
        from_attributes = True


class JogoResponse(BaseModel):
    data: date
    adversario: str
    casa_ou_fora: str
    resultado: str
    gols_time: int
    gols_adversario: int
    escanteios_time: int
    escanteios_adversario: int
    escanteios_1t_time: int
    escanteios_1t_adversario: int
    escanteios_2t_time: int
    escanteios_2t_adversario: int
    chutes_time: int
    chutes_adversario: int
    chutes_1t_time: int
    chutes_1t_adversario: int
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
    sequencia_recente: List[str]