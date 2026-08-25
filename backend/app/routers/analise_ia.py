import json
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.database import SessionLocal
from app.models.partida import Partida
from app.models.analise_ia import AnaliseIAPartida
from app.schemas.analise_ia import AnaliseIAResponse, BilheteSimples, BilheteMultipla
from app.services.analise_ia import gerar_analise, gerar_dicas, IANaoConfiguradaError
from app.services.analise_mercado import montar_pernas, montar_bilhetes
from app.services.medias import ultimo_jogo_finalizado
from app.services.destaques import (
    calcular_destaques_time_e_totais,
    calcular_destaques_jogadores_confronto,
)

router = APIRouter(prefix="/partidas", tags=["Análise IA"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _calcular_destaques_e_bilhetes(db, partida):
    """Roda o calculo pesado (varias queries) de destaques/bilhetes pra
    um confronto -- so chamado quando o cache em AnaliseIAPartida esta
    ausente ou invalido (ver mandante_ultimo_jogo/visitante_ultimo_jogo
    em obter_analise)."""
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

    destaques_jogadores_mandante, destaques_jogadores_visitante = calcular_destaques_jogadores_confronto(
        db, partida.time_mandante_id, partida.time_visitante_id
    )

    return {
        "destaques_mandante": destaques_mandante,
        "destaques_visitante": destaques_visitante,
        "destaques_jogadores_mandante": destaques_jogadores_mandante,
        "destaques_jogadores_visitante": destaques_jogadores_visitante,
        "destaques_totais": pernas_totais,
        "bilhete_simples": bilhete_simples_dict,
        "bilhete_multipla": bilhete_multipla_dict,
    }


@router.get("/{partida_id}/analise", response_model=AnaliseIAResponse)
def obter_analise(partida_id: int, db: Session = Depends(get_db)):
    # joinedload evita 2 queries extras (lazy load de time_mandante/
    # time_visitante na primeira vez que .nome e' acessado mais abaixo).
    partida = (
        db.query(Partida)
        .options(joinedload(Partida.time_mandante), joinedload(Partida.time_visitante))
        .filter(Partida.id == partida_id)
        .first()
    )
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

    # Os destaques dos ultimos N jogos de cada time so mudam quando esse
    # time joga uma partida nova -- comparando essa data com a que estava
    # valendo quando o cache foi calculado, da pra saber se o
    # destaques_json cacheado ainda reflete os mesmos jogos (e pular todo
    # o recalculo, que sozinho ja soma 6-7 queries).
    mandante_ultimo_jogo = ultimo_jogo_finalizado(db, partida.time_mandante_id)
    visitante_ultimo_jogo = ultimo_jogo_finalizado(db, partida.time_visitante_id)

    existente = db.query(AnaliseIAPartida).filter(AnaliseIAPartida.partida_id == partida_id).first()
    cache_valido = (
        existente is not None
        and existente.destaques_json is not None
        and existente.mandante_ultimo_jogo == mandante_ultimo_jogo
        and existente.visitante_ultimo_jogo == visitante_ultimo_jogo
    )

    if cache_valido:
        calculado = json.loads(existente.destaques_json)
    else:
        calculado = _calcular_destaques_e_bilhetes(db, partida)

    bilhete_simples_dict = calculado["bilhete_simples"]
    bilhete_multipla_dict = calculado["bilhete_multipla"]

    base = dict(
        destaques_mandante=calculado["destaques_mandante"],
        destaques_visitante=calculado["destaques_visitante"],
        destaques_jogadores_mandante=calculado["destaques_jogadores_mandante"],
        destaques_jogadores_visitante=calculado["destaques_jogadores_visitante"],
        destaques_totais=calculado["destaques_totais"],
        bilhete_simples=BilheteSimples(**bilhete_simples_dict) if bilhete_simples_dict else None,
        bilhete_multipla=BilheteMultipla(**bilhete_multipla_dict) if bilhete_multipla_dict else None,
    )

    # Resumo/dicas da IA sao gerados junto com o destaques_json (mesma
    # condicao de cache: se os jogos considerados nao mudaram, o texto
    # que justifica o bilhete tambem continua valendo).
    if cache_valido:
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
        dicas, _ = gerar_dicas(calculado["destaques_totais"])
    except IANaoConfiguradaError:
        return AnaliseIAResponse(partida_id=partida_id, disponivel=False, **base)

    destaques_json = json.dumps(calculado)
    if existente:
        existente.texto = resumo
        existente.dicas = dicas
        existente.modelo = modelo
        existente.destaques_json = destaques_json
        existente.mandante_ultimo_jogo = mandante_ultimo_jogo
        existente.visitante_ultimo_jogo = visitante_ultimo_jogo
        nova = existente
    else:
        nova = AnaliseIAPartida(
            partida_id=partida_id,
            texto=resumo,
            dicas=dicas,
            modelo=modelo,
            destaques_json=destaques_json,
            mandante_ultimo_jogo=mandante_ultimo_jogo,
            visitante_ultimo_jogo=visitante_ultimo_jogo,
        )
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
