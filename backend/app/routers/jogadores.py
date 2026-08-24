from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import SessionLocal
from app.models.jogador import Jogador
from app.schemas.jogador import JogadorRankingResponse, JogadorPerfilResponse, JogoJogadorResponse
from app.services.jogadores import calcular_ranking, obter_ultimos_jogos_jogador, STATS_VALIDAS

router = APIRouter(prefix="/jogadores", tags=["Jogadores"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/ranking/{stat}", response_model=JogadorRankingResponse)
def ranking_por_stat(
    stat: str,
    limit: int = 20,
    mando: Optional[str] = None,
    time_id: Optional[int] = None,
    campeonato_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    ranking = calcular_ranking(db, stat, limit, mando, time_id, campeonato_id)
    if ranking is None:
        raise HTTPException(status_code=404, detail="Estatistica invalida")
    return {"stat": stat, "ranking": ranking}


@router.get("/{jogador_id}", response_model=JogadorPerfilResponse)
def perfil_jogador(jogador_id: int, db: Session = Depends(get_db)):
    jogador = db.query(Jogador).filter(Jogador.id == jogador_id).first()
    if not jogador:
        raise HTTPException(status_code=404, detail="Jogador nao encontrado")
    return {
        "id": jogador.id,
        "nome": jogador.nome,
        "posicao": jogador.posicao,
        "time_id": jogador.time_id,
        "time_nome": jogador.time.nome if jogador.time else None,
    }


@router.get("/{jogador_id}/jogos", response_model=List[JogoJogadorResponse])
def jogos_jogador(
    jogador_id: int, quantidade: int = 10, mando: Optional[str] = None, db: Session = Depends(get_db)
):
    jogador = db.query(Jogador).filter(Jogador.id == jogador_id).first()
    if not jogador:
        raise HTTPException(status_code=404, detail="Jogador nao encontrado")
    return obter_ultimos_jogos_jogador(db, jogador_id, quantidade, mando)
