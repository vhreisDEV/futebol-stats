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


@router.get("/{partida_id}", response_model=PartidaDetalheResponse)
def obter_partida(partida_id: int, db: Session = Depends(get_db)):
    partida = db.query(Partida).filter(Partida.id == partida_id).first()
    if not partida:
        raise HTTPException(status_code=404, detail="Partida nao encontrada")

    return PartidaDetalheResponse(
        id=partida.id,
        data=partida.data,
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
