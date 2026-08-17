from pydantic import BaseModel
from datetime import date
from typing import List, Optional


class JogadorRankingItem(BaseModel):
    jogador_id: int
    nome: str
    posicao: Optional[str]
    time_id: Optional[int]
    time_nome: Optional[str]
    jogos: int
    total: int
    media: float


class JogadorRankingResponse(BaseModel):
    stat: str
    ranking: List[JogadorRankingItem]


class JogadorPerfilResponse(BaseModel):
    id: int
    nome: str
    posicao: Optional[str]
    time_id: Optional[int]
    time_nome: Optional[str]


class JogoJogadorResponse(BaseModel):
    id: int
    partida_id: int
    data: date
    adversario: str
    casa_ou_fora: str
    minutos_jogados: Optional[int]
    gols: int
    assistencias: int
    chutes: Optional[int]
    chutes_gol: Optional[int]
    desarmes: Optional[int]
    faltas_cometidas: Optional[int]
    faltas_sofridas: Optional[int]
    cartoes_amarelos: int
    cartoes_vermelhos: int
