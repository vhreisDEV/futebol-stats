from pydantic import BaseModel
from typing import List


class LinhaClassificacao(BaseModel):
    posicao: int
    time_id: int
    time: str
    pontos: int
    jogos: int
    vitorias: int
    empates: int
    derrotas: int
    gols_pro: int
    gols_contra: int
    saldo_gols: int


class ClassificacaoResponse(BaseModel):
    classificacao: List[LinhaClassificacao]
