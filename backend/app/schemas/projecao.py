from typing import Optional
from pydantic import BaseModel


class GolsEsperados(BaseModel):
    mandante: Optional[float]
    visitante: Optional[float]


class ProbabilidadeResultado(BaseModel):
    vitoria_mandante: Optional[float]
    empate: Optional[float]
    vitoria_visitante: Optional[float]


class EscanteiosEsperados(BaseModel):
    mandante: Optional[float]
    visitante: Optional[float]
    total: Optional[float]
    linha_referencia: Optional[float]
    tendencia: Optional[str]


class CartoesEsperados(BaseModel):
    amarelos_mandante: Optional[float]
    amarelos_visitante: Optional[float]
    vermelhos_mandante: Optional[float]
    vermelhos_visitante: Optional[float]
    total: Optional[float]
    linha_referencia: Optional[float]
    tendencia: Optional[str]


class ChutesEsperados(BaseModel):
    totais_mandante: Optional[float]
    totais_visitante: Optional[float]
    total_geral: Optional[float]
    linha_referencia_geral: Optional[float]
    tendencia_geral: Optional[str]
    ao_gol_mandante: Optional[float]
    ao_gol_visitante: Optional[float]
    total_ao_gol: Optional[float]
    linha_referencia_ao_gol: Optional[float]
    tendencia_ao_gol: Optional[str]
    primeiro_tempo_mandante: Optional[float]
    primeiro_tempo_visitante: Optional[float]


class ProjecaoResponse(BaseModel):
    time_mandante: str
    time_visitante: str
    data_referencia: str
    gols: GolsEsperados
    resultado: ProbabilidadeResultado
    escanteios: EscanteiosEsperados
    cartoes: CartoesEsperados
    chutes: ChutesEsperados
