from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.partida import Partida
from app.schemas.rodada import RodadaResponse, PartidaRodadaResponse

router = APIRouter(prefix="/rodadas", tags=["Rodadas"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{numero}", response_model=RodadaResponse)
def obter_rodada(numero: int, db: Session = Depends(get_db)):
    partidas = (
        db.query(Partida)
        .filter(Partida.rodada == numero)
        .order_by(Partida.data)
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
                time_mandante=p.time_mandante.nome,
                time_visitante=p.time_visitante.nome,
                gols_mandante=p.gols_mandante,
                gols_visitante=p.gols_visitante,
            )
            for p in partidas
        ],
    )
