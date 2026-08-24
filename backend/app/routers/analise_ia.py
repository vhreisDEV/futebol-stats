from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.partida import Partida
from app.models.analise_ia import AnaliseIAPartida
from app.schemas.destaque import Destaque
from app.schemas.analise_ia import AnaliseIAResponse, MelhorMercado
from app.services.analise_ia import gerar_analise, IANaoConfiguradaError
from app.services.analise_mercado import escolher_melhor_mercado
from app.services.destaques import calcular_destaques_time

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

    # A analise (mercados + previa da IA) so existe pra partida que ainda
    # vai acontecer -- nao faz sentido "prever" um jogo ja disputado.
    if partida.status == "finalizada":
        return AnaliseIAResponse(partida_id=partida_id, disponivel=False)

    referencia = partida.data or date.today()
    destaques_mandante = calcular_destaques_time(db, partida.time_mandante_id, "mandante", referencia)
    destaques_visitante = calcular_destaques_time(db, partida.time_visitante_id, "visitante", referencia)
    melhor = escolher_melhor_mercado(
        partida.time_mandante.nome, destaques_mandante, partida.time_visitante.nome, destaques_visitante
    )

    base = dict(
        destaques_mandante=[Destaque(**d) for d in destaques_mandante],
        destaques_visitante=[Destaque(**d) for d in destaques_visitante],
        melhor_mercado=MelhorMercado(**melhor) if melhor else None,
    )

    existente = db.query(AnaliseIAPartida).filter(AnaliseIAPartida.partida_id == partida_id).first()
    if existente:
        return AnaliseIAResponse(
            partida_id=partida_id,
            disponivel=True,
            texto=existente.texto,
            gerado_em=existente.criado_em.isoformat() if existente.criado_em else None,
            **base,
        )

    try:
        texto, modelo = gerar_analise(partida, destaques_mandante, destaques_visitante)
    except IANaoConfiguradaError:
        return AnaliseIAResponse(partida_id=partida_id, disponivel=False, **base)

    nova = AnaliseIAPartida(partida_id=partida_id, texto=texto, modelo=modelo)
    db.add(nova)
    db.commit()
    db.refresh(nova)

    return AnaliseIAResponse(
        partida_id=partida_id,
        disponivel=True,
        texto=nova.texto,
        gerado_em=nova.criado_em.isoformat() if nova.criado_em else None,
        **base,
    )
