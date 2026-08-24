from typing import List, Optional
from pydantic import BaseModel

from app.schemas.destaque import Destaque, DestaqueJogador


class Perna(BaseModel):
    time: str  # "mandante" ou "visitante"
    nome_time: str
    destaque: Destaque


class BilheteSimples(BaseModel):
    perna: Perna
    confianca: float  # 0 a 10 (= taxa de acerto * 10)


class BilheteMultipla(BaseModel):
    pernas: List[Perna]
    confianca_combinada: float  # 0 a 10 (= produto das taxas * 10)


class AnaliseIAResponse(BaseModel):
    partida_id: int
    disponivel: bool
    dentro_da_janela: bool = True
    resumo: Optional[str] = None
    gerado_em: Optional[str] = None
    destaques_mandante: List[Destaque] = []
    destaques_visitante: List[Destaque] = []
    destaques_jogadores_mandante: List[DestaqueJogador] = []
    destaques_jogadores_visitante: List[DestaqueJogador] = []
    destaques_totais: List[Perna] = []
    dicas: Optional[str] = None
    bilhete_simples: Optional[BilheteSimples] = None
    bilhete_multipla: Optional[BilheteMultipla] = None
