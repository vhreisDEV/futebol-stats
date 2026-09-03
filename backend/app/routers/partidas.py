from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.partida import Partida
from app.schemas.partida import PartidaDetalheResponse

router = APIRouter(prefix="/partidas", tags=["Partidas"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/proxima")
def obter_proxima_partida(
    campeonato_id: Optional[int] = None, time_id: Optional[int] = None, db: Session = Depends(get_db)
):
    """
    Acha a proxima partida agendada (a de data mais proxima), pra linkar
    direto a Analise IA dela sem precisar de uma pagina de listagem por
    rodada -- ou, com `time_id`, o proximo jogo de um time especifico
    (usado pra dar contexto de "proximo adversario" na grade de
    estatistica por time). So devolve o id -- quem chama busca o resto
    via /partidas/{id}.
    """
    query = db.query(Partida).filter(Partida.status == "agendada")
    if campeonato_id is not None:
        query = query.filter(Partida.campeonato_id == campeonato_id)
    if time_id is not None:
        query = query.filter((Partida.time_mandante_id == time_id) | (Partida.time_visitante_id == time_id))

    partida = query.order_by(
        Partida.data.is_(None), Partida.data, Partida.hora.is_(None), Partida.hora
    ).first()

    if not partida:
        raise HTTPException(status_code=404, detail="Nenhuma partida agendada encontrada")

    return {"id": partida.id}


@router.get("/{partida_id}", response_model=PartidaDetalheResponse)
def obter_partida(partida_id: int, db: Session = Depends(get_db)):
    partida = db.query(Partida).filter(Partida.id == partida_id).first()
    if not partida:
        raise HTTPException(status_code=404, detail="Partida nao encontrada")

    return PartidaDetalheResponse(
        id=partida.id,
        campeonato_id=partida.campeonato_id,
        data=partida.data,
        hora=partida.hora,
        status=partida.status,
        rodada=partida.rodada,
        time_mandante_id=partida.time_mandante_id,
        time_mandante=partida.time_mandante.nome,
        time_visitante_id=partida.time_visitante_id,
        time_visitante=partida.time_visitante.nome,
        gols_mandante=partida.gols_mandante,
        gols_visitante=partida.gols_visitante,
        escanteios_mandante=partida.escanteios_mandante,
        escanteios_visitante=partida.escanteios_visitante,
        chutes_mandante=partida.chutes_mandante,
        chutes_visitante=partida.chutes_visitante,
        chutes_gol_mandante=partida.chutes_gol_mandante,
        chutes_gol_visitante=partida.chutes_gol_visitante,
        cartoes_amarelos_mandante=partida.cartoes_amarelos_mandante,
        cartoes_amarelos_visitante=partida.cartoes_amarelos_visitante,
        cartoes_vermelhos_mandante=partida.cartoes_vermelhos_mandante,
        cartoes_vermelhos_visitante=partida.cartoes_vermelhos_visitante,
    )
