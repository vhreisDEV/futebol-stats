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

class EstatisticasResponse(BaseModel):
    total_jogos: int
    vitorias: int
    empates: int
    derrotas: int
    gols_marcados: int
    gols_sofridos: int
    media_gols: float
    sequencia_recente: List[str]

