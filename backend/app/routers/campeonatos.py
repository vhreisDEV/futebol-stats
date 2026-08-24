from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.campeonato import Campeonato
from app.models.partida import Partida
from app.models.time import Time
from app.schemas.campeonato import CampeonatoResponse, ListaCampeonatosResponse

router = APIRouter(prefix="/campeonatos", tags=["Campeonatos"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _montar_response(db, c):
    rodada_atual = (
        db.query(func.max(Partida.rodada))
        .filter(Partida.campeonato_id == c.id, Partida.status == "finalizada")
        .scalar()
    )
    total_times = db.query(Time).filter(Time.campeonato_id == c.id).count()

    return CampeonatoResponse(
        id=c.id,
        nome=c.nome,
        pais_nome=c.pais_nome,
        pais_codigo=c.pais_codigo,
        temporada=c.temporada,
        rodadas_total=c.rodadas_total,
        ativo=c.ativo,
        rodada_atual=rodada_atual,
        total_times=total_times,
    )


@router.get("/", response_model=ListaCampeonatosResponse)
def listar_campeonatos(db: Session = Depends(get_db)):
    campeonatos = db.query(Campeonato).filter(Campeonato.ativo.is_(True)).order_by(Campeonato.id).all()
    return ListaCampeonatosResponse(campeonatos=[_montar_response(db, c) for c in campeonatos])


@router.get("/{campeonato_id}", response_model=CampeonatoResponse)
def obter_campeonato(campeonato_id: int, db: Session = Depends(get_db)):
    campeonato = db.query(Campeonato).filter(Campeonato.id == campeonato_id).first()
    if not campeonato:
        raise HTTPException(status_code=404, detail="Campeonato nao encontrado")
    return _montar_response(db, campeonato)
