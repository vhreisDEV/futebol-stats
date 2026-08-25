from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.partida import Partida
from app.models.analise_ia import AnaliseIAPartida
from app.schemas.analise_ia import AnaliseIAResponse, BilheteSimples, BilheteMultipla
from app.services.analise_ia import gerar_analise, gerar_dicas, IANaoConfiguradaError
from app.services.analise_mercado import montar_pernas, montar_bilhetes
from app.services.destaques import (
    calcular_destaques_time_e_totais,
    calcular_destaques_jogadores_time,
)

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

    # A analise (mercados + bilhetes + resumo/dicas da IA) so existe pra
    # partida que ainda vai acontecer -- nao faz sentido "prever" um jogo
    # ja disputado.
    if partida.status == "finalizada":
        return AnaliseIAResponse(partida_id=partida_id, disponivel=False)

    # Feature nova (rollout controlado): so libera pra rodada atual ou a
    # proxima -- rodadas mais distantes ainda nao mostram nada, mesmo que
    # ja estejam com data marcada. Sem partida finalizada ainda nesse
    # campeonato (rodada_atual None), libera geral (caso raro, inicio de
    # temporada).
    rodada_atual = (
        db.query(func.max(Partida.rodada))
        .filter(Partida.status == "finalizada", Partida.campeonato_id == partida.campeonato_id)
        .scalar()
    )
    dentro_da_janela = (
        rodada_atual is None or partida.rodada is None or partida.rodada <= rodada_atual + 1
    )
    if not dentro_da_janela:
        return AnaliseIAResponse(partida_id=partida_id, disponivel=False, dentro_da_janela=False)

    referencia = partida.data or date.today()
    destaques_mandante, destaques_totais_mandante = calcular_destaques_time_e_totais(
        db, partida.time_mandante_id, "mandante", referencia
    )
    destaques_visitante, destaques_totais_visitante = calcular_destaques_time_e_totais(
        db, partida.time_visitante_id, "visitante", referencia
    )

    pernas = montar_pernas(
        partida.time_mandante.nome, destaques_mandante, partida.time_visitante.nome, destaques_visitante
    )
    bilhete_simples_dict, bilhete_multipla_dict = montar_bilhetes(pernas)

    pernas_totais = montar_pernas(
        partida.time_mandante.nome, destaques_totais_mandante, partida.time_visitante.nome, destaques_totais_visitante
    )

    # Bilhetes e destaques sao calculados na hora (gratis, sem IA) e sempre
    # aparecem -- so o resumo/dicas em texto dependem da chave do Gemini
    # configurada.
    base = dict(
        destaques_mandante=destaques_mandante,
        destaques_visitante=destaques_visitante,
        destaques_jogadores_mandante=calcular_destaques_jogadores_time(db, partida.time_mandante_id),
        destaques_jogadores_visitante=calcular_destaques_jogadores_time(db, partida.time_visitante_id),
        destaques_totais=pernas_totais,
        bilhete_simples=BilheteSimples(**bilhete_simples_dict) if bilhete_simples_dict else None,
        bilhete_multipla=BilheteMultipla(**bilhete_multipla_dict) if bilhete_multipla_dict else None,
    )

    existente = db.query(AnaliseIAPartida).filter(AnaliseIAPartida.partida_id == partida_id).first()
    if existente:
        return AnaliseIAResponse(
            partida_id=partida_id,
            disponivel=True,
            resumo=existente.texto,
            dicas=existente.dicas,
            gerado_em=existente.criado_em.isoformat() if existente.criado_em else None,
            **base,
        )

    try:
        resumo, modelo = gerar_analise(bilhete_simples_dict, bilhete_multipla_dict)
        dicas, _ = gerar_dicas(pernas_totais)
    except IANaoConfiguradaError:
        return AnaliseIAResponse(partida_id=partida_id, disponivel=False, **base)

    nova = AnaliseIAPartida(partida_id=partida_id, texto=resumo, dicas=dicas, modelo=modelo)
    db.add(nova)
    db.commit()
    db.refresh(nova)

    return AnaliseIAResponse(
        partida_id=partida_id,
        disponivel=True,
        resumo=nova.texto,
        dicas=nova.dicas,
        gerado_em=nova.criado_em.isoformat() if nova.criado_em else None,
        **base,
    )
