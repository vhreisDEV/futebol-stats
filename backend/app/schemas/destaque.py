from typing import List
from pydantic import BaseModel


class Destaque(BaseModel):
    stat: str
    label: str
    tipo: str  # "quantidade" ou "booleano"
    linha: float
    acertos: int
    total: int
    taxa: float
    sequencia: List[int]
    media: float


class DestaqueJogador(BaseModel):
    jogador_id: int
    nome: str
    posicao: str | None
    destaques: List[Destaque]


class JogoComDestaques(BaseModel):
    partida_id: int
    data: str | None
    rodada: int
    time_mandante_id: int
    time_mandante: str
    time_visitante_id: int
    time_visitante: str
    destaques_mandante: List[Destaque]
    destaques_visitante: List[Destaque]
    destaques_jogadores_mandante: List[DestaqueJogador] = []
    destaques_jogadores_visitante: List[DestaqueJogador] = []


class DestaquesRodadaResponse(BaseModel):
    rodada: int
    jogos: List[JogoComDestaques]
