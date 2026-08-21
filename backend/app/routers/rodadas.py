from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.partida import Partida
from app.schemas.rodada import RodadaResponse, PartidaRodadaResponse, RodadaAtualResponse

router = APIRouter(prefix="/rodadas", tags=["Rodadas"])

TOTAL_RODADAS_BRASILEIRAO = 38


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/atual", response_model=RodadaAtualResponse)
def obter_rodada_atual(db: Session = Depends(get_db)):
    # So considera rodadas com pelo menos uma partida ja finalizada -- senao,
    # pre-cadastrar o calendario completo (agendada/adiada) adiantaria a
    # "rodada atual" para rodadas que ainda nem comecaram.
    maior_rodada = (
        db.query(func.max(Partida.rodada)).filter(Partida.status == "finalizada").scalar()
    )

    if maior_rodada is None:
        raise HTTPException(status_code=404, detail="Nenhuma partida com rodada cadastrada")

    return RodadaAtualResponse(rodada_atual=maior_rodada, rodada_maxima=TOTAL_RODADAS_BRASILEIRAO)


@router.get("/{numero}", response_model=RodadaResponse)
def obter_rodada(numero: int, db: Session = Depends(get_db)):
    partidas = (
        db.query(Partida)
        .filter(Partida.rodada == numero)
        .order_by(Partida.data.is_(None), Partida.data, Partida.hora.is_(None), Partida.hora)
        .all()
    )

    if not partidas:
        raise HTTPException(status_code=404, detail="Nenhuma partida encontrada para essa rodada")

    return RodadaResponse(
        rodada=numero,
        partidas=[
            PartidaRodadaResponse(
                id=p.id,
                data=p.data,
                hora=p.hora,
                status=p.status,
                time_mandante_id=p.time_mandante_id,
                time_mandante=p.time_mandante.nome,
                time_visitante_id=p.time_visitante_id,
                time_visitante=p.time_visitante.nome,
                gols_mandante=p.gols_mandante,
                gols_visitante=p.gols_visitante,
            )
            for p in partidas
        ],
    )
