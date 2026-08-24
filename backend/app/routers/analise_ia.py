from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.partida import Partida
from app.models.analise_ia import AnaliseIAPartida
from app.schemas.analise_ia import AnaliseIAResponse
from app.services.analise_ia import gerar_analise, IANaoConfiguradaError

router = APIRouter(prefix="/partidas", tags=["Análise IA"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{partida_id}/analise", response_model=AnaliseIAResponse)
def obter_analise(partida_id: int, db: Session = Depends(get_db)):
    partida = db.query(Partida).filter(Partida.id == partida_id).first()
    if not partida:
        raise HTTPException(status_code=404, detail="Partida nao encontrada")

    existente = db.query(AnaliseIAPartida).filter(AnaliseIAPartida.partida_id == partida_id).first()
    if existente:
        return AnaliseIAResponse(
            partida_id=partida_id,
            disponivel=True,
            texto=existente.texto,
            gerado_em=existente.criado_em.isoformat() if existente.criado_em else None,
        )

    # So gera previa pra partida que ainda vai acontecer -- nao faz sentido
    # "prever" um jogo que ja foi disputado.
    if partida.status == "finalizada":
        return AnaliseIAResponse(partida_id=partida_id, disponivel=False)

    try:
        texto, modelo = gerar_analise(db, partida)
    except IANaoConfiguradaError:
        return AnaliseIAResponse(partida_id=partida_id, disponivel=False)

    nova = AnaliseIAPartida(partida_id=partida_id, texto=texto, modelo=modelo)
    db.add(nova)
    db.commit()
    db.refresh(nova)

    return AnaliseIAResponse(
        partida_id=partida_id,
        disponivel=True,
        texto=nova.texto,
        gerado_em=nova.criado_em.isoformat() if nova.criado_em else None,
    )
