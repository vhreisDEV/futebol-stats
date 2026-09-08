from typing import List, Optional
from pydantic import BaseModel


class CampeonatoResponse(BaseModel):
    id: int
    nome: str
    pais_nome: str
    pais_codigo: str
    temporada: int
    temporada_label: str
    rodadas_total: Optional[int]
    ativo: bool
    rodada_atual: Optional[int] = None
    total_times: int = 0
    # Menor numero de jogos finalizados entre todos os times da liga --
    # diferente de rodada_atual (MAX das rodadas), que uma unica partida
    # remarcada pra rodada futura ja infla sem que o resto dos times
    # tenha jogado tanto. Usado pra liberar Previsao/Dicas/Comparar so
    # quando TODO time realmente tem o minimo de jogos de historico.
    jogos_minimo_time: Optional[int] = None


class ListaCampeonatosResponse(BaseModel):
    campeonatos: List[CampeonatoResponse]
