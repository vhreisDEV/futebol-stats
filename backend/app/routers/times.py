from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import SessionLocal
from app.models.time import Time
from app.schemas.time import TimeBase, JogoResponse, EstatisticasResponse
from app.services.estatisticas import obter_ultimos_jogos, obter_jogos_ate_rodada, calcular_estatisticas

router = APIRouter(prefix="/times", tags=["Times"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[TimeBase])
def listar_times(db: Session = Depends(get_db)):
    return db.query(Time).order_by(Time.nome).all()

@router.get("/{time_id}/jogos", response_model=List[JogoResponse])
def listar_ultimos_jogos(
    time_id: int, quantidade: int = 10, mando: Optional[str] = None, db: Session = Depends(get_db)
):
    time = db.query(Time).filter(Time.id == time_id).first()
    if not time:
        raise HTTPException(status_code=404, detail="Time nao encontrado")
    return obter_ultimos_jogos(db, time_id, quantidade, mando)

@router.get("/{time_id}/estatisticas", response_model=EstatisticasResponse)
def listar_estatisticas(
    time_id: int, quantidade: int = 10, mando: Optional[str] = None, db: Session = Depends(get_db)
):
    time = db.query(Time).filter(Time.id == time_id).first()
    if not time:
        raise HTTPException(status_code=404, detail="Time nao encontrado")
    jogos = obter_ultimos_jogos(db, time_id, quantidade, mando)
    return calcular_estatisticas(jogos)

@router.get("/{time_id}/estatisticas/ate-rodada/{numero}", response_model=EstatisticasResponse)
def listar_estatisticas_ate_rodada(time_id: int, numero: int, db: Session = Depends(get_db)):
    time = db.query(Time).filter(Time.id == time_id).first()
    if not time:
        raise HTTPException(status_code=404, detail="Time nao encontrado")
    jogos = obter_jogos_ate_rodada(db, time_id, numero)
    return calcular_estatisticas(jogos)