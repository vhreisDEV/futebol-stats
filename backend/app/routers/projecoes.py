from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.time import Time
from app.schemas.projecao import (
    ProjecaoResponse,
    GolsEsperados,
    ProbabilidadeResultado,
    EscanteiosEsperados,
    CartoesEsperados,
    ChutesEsperados,
)
from app.services.gols_esperados import calcular_gols_esperados
from app.services.probabilidade_resultado import calcular_probabilidade_resultado
from app.services.escanteios_esperados import calcular_escanteios_esperados
from app.services.cartoes_esperados import calcular_cartoes_esperados
from app.services.chutes_esperados import calcular_chutes_esperados

router = APIRouter(prefix="/projecoes", tags=["Projeções"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{mandante_id}/{visitante_id}", response_model=ProjecaoResponse)
def obter_projecao(
    mandante_id: int,
    visitante_id: int,
    data_referencia: Optional[date] = Query(
        None, description="Data de referência para a projeção. Padrão: hoje."
    ),
    db: Session = Depends(get_db),
):
    if mandante_id == visitante_id:
        raise HTTPException(status_code=400, detail="Mandante e visitante devem ser times diferentes")

    time_mandante = db.query(Time).filter(Time.id == mandante_id).first()
    if not time_mandante:
        raise HTTPException(status_code=404, detail="Time mandante nao encontrado")

    time_visitante = db.query(Time).filter(Time.id == visitante_id).first()
    if not time_visitante:
        raise HTTPException(status_code=404, detail="Time visitante nao encontrado")

    referencia = data_referencia or date.today()

    gols = calcular_gols_esperados(db, mandante_id, visitante_id, referencia)
    resultado = calcular_probabilidade_resultado(db, mandante_id, visitante_id, referencia)
    escanteios = calcular_escanteios_esperados(db, mandante_id, visitante_id, referencia)
    cartoes = calcular_cartoes_esperados(db, mandante_id, visitante_id, referencia)
    chutes = calcular_chutes_esperados(db, mandante_id, visitante_id, referencia)

    return ProjecaoResponse(
        time_mandante=time_mandante.nome,
        time_visitante=time_visitante.nome,
        data_referencia=str(referencia),
        gols=GolsEsperados(
            mandante=gols.get("gols_esperados_mandante"),
            visitante=gols.get("gols_esperados_visitante"),
        ),
        resultado=ProbabilidadeResultado(
            vitoria_mandante=resultado.get("probabilidade_vitoria_mandante"),
            empate=resultado.get("probabilidade_empate"),
            vitoria_visitante=resultado.get("probabilidade_vitoria_visitante"),
        ),
        escanteios=EscanteiosEsperados(
            mandante=escanteios.get("escanteios_esperados_mandante"),
            visitante=escanteios.get("escanteios_esperados_visitante"),
            total=escanteios.get("total_esperado"),
            linha_referencia=escanteios.get("linha_referencia"),
            tendencia=escanteios.get("tendencia"),
        ),
        cartoes=CartoesEsperados(
            amarelos_mandante=cartoes.get("cartoes_amarelos_esperados_mandante"),
            amarelos_visitante=cartoes.get("cartoes_amarelos_esperados_visitante"),
            vermelhos_mandante=cartoes.get("cartoes_vermelhos_esperados_mandante"),
            vermelhos_visitante=cartoes.get("cartoes_vermelhos_esperados_visitante"),
            total=cartoes.get("total_cartoes_esperado"),
            linha_referencia=cartoes.get("linha_referencia"),
            tendencia=cartoes.get("tendencia"),
        ),
        chutes=ChutesEsperados(
            totais_mandante=chutes.get("chutes_totais_esperados_mandante"),
            totais_visitante=chutes.get("chutes_totais_esperados_visitante"),
            total_geral=chutes.get("total_geral_esperado"),
            linha_referencia_geral=chutes.get("linha_referencia_geral"),
            tendencia_geral=chutes.get("tendencia_geral"),
            ao_gol_mandante=chutes.get("chutes_gol_esperados_mandante"),
            ao_gol_visitante=chutes.get("chutes_gol_esperados_visitante"),
            total_ao_gol=chutes.get("total_ao_gol_esperado"),
            linha_referencia_ao_gol=chutes.get("linha_referencia_ao_gol"),
            tendencia_ao_gol=chutes.get("tendencia_ao_gol"),
            primeiro_tempo_mandante=chutes.get("chutes_1t_esperados_mandante"),
            primeiro_tempo_visitante=chutes.get("chutes_1t_esperados_visitante"),
        ),
    )
