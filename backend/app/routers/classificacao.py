from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.schemas.classificacao import ClassificacaoResponse, LinhaClassificacao
from app.services.classificacao import calcular_classificacao

router = APIRouter(prefix="/classificacao", tags=["Classificação"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=ClassificacaoResponse)
def obter_classificacao(
    ate_rodada: Optional[int] = Query(
        None, description="Considera apenas jogos ate esta rodada. Padrao: todos os jogos ja importados."
    ),
    campeonato_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    tabela = calcular_classificacao(db, ate_rodada, campeonato_id)
    return ClassificacaoResponse(classificacao=[LinhaClassificacao(**linha) for linha in tabela])
