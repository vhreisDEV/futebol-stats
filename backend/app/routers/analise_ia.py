from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.partida import Partida
from app.models.analise_ia import AnaliseIAPartida
from app.schemas.analise_ia import AnaliseIAResponse, BilheteSimples, BilheteMultipla
from app.services.analise_ia import gerar_analise, IANaoConfiguradaError
from app.services.analise_mercado import montar_pernas, montar_bilhetes
from app.services.destaques import calcular_destaques_time, calcular_destaques_jogadores_time

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

    # A analise (mercados + bilhetes + resumo da IA) so existe pra partida
    # que ainda vai acontecer -- nao faz sentido "prever" um jogo ja
    # disputado.
    if partida.status == "finalizada":
        return AnaliseIAResponse(partida_id=partida_id, disponivel=False)

    referencia = partida.data or date.today()
    destaques_mandante = calcular_destaques_time(db, partida.time_mandante_id, "mandante", referencia)
    destaques_visitante = calcular_destaques_time(db, partida.time_visitante_id, "visitante", referencia)

    pernas = montar_pernas(
        partida.time_mandante.nome, destaques_mandante, partida.time_visitante.nome, destaques_visitante
    )
    bilhete_simples_dict, bilhete_multipla_dict = montar_bilhetes(pernas)

    # Bilhetes e destaques sao calculados na hora (gratis, sem IA) e sempre
    # aparecem -- so o resumo em texto depende da chave do Gemini
    # configurada.
    base = dict(
        destaques_mandante=destaques_mandante,
        destaques_visitante=destaques_visitante,
        destaques_jogadores_mandante=calcular_destaques_jogadores_time(db, partida.time_mandante_id),
        destaques_jogadores_visitante=calcular_destaques_jogadores_time(db, partida.time_visitante_id),
        bilhete_simples=BilheteSimples(**bilhete_simples_dict) if bilhete_simples_dict else None,
        bilhete_multipla=BilheteMultipla(**bilhete_multipla_dict) if bilhete_multipla_dict else None,
    )

    existente = db.query(AnaliseIAPartida).filter(AnaliseIAPartida.partida_id == partida_id).first()
    if existente:
        return AnaliseIAResponse(
            partida_id=partida_id,
            disponivel=True,
            resumo=existente.texto,
            gerado_em=existente.criado_em.isoformat() if existente.criado_em else None,
            **base,
        )

    try:
        resumo, modelo = gerar_analise(bilhete_simples_dict, bilhete_multipla_dict)
    except IANaoConfiguradaError:
        return AnaliseIAResponse(partida_id=partida_id, disponivel=False, **base)

    nova = AnaliseIAPartida(partida_id=partida_id, texto=resumo, modelo=modelo)
    db.add(nova)
    db.commit()
    db.refresh(nova)

    return AnaliseIAResponse(
        partida_id=partida_id,
        disponivel=True,
        resumo=nova.texto,
        gerado_em=nova.criado_em.isoformat() if nova.criado_em else None,
        **base,
    )
