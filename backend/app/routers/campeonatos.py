from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.campeonato import Campeonato
from app.schemas.campeonato import CampeonatoResponse, ListaCampeonatosResponse

router = APIRouter(prefix="/campeonatos", tags=["Campeonatos"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=ListaCampeonatosResponse)
def listar_campeonatos(db: Session = Depends(get_db)):
    campeonatos = db.query(Campeonato).filter(Campeonato.ativo.is_(True)).order_by(Campeonato.id).all()
    return ListaCampeonatosResponse(
        campeonatos=[
            CampeonatoResponse(
                id=c.id,
                nome=c.nome,
                pais_nome=c.pais_nome,
                pais_codigo=c.pais_codigo,
                temporada=c.temporada,
                rodadas_total=c.rodadas_total,
                ativo=c.ativo,
            )
            for c in campeonatos
        ]
    )
