"""
Testa app/routers/analise_ia.py::obter_analise contra um banco SQLite
isolado em memoria -- cobre o bug real encontrado 2026-09-01: o Gemini
retornou 503 ("high demand") e a rota quebrava com 500 pro usuario final,
porque so' capturavamos IANaoConfiguradaError, nunca uma falha
transitoria da API. Agora uma falha do Gemini degrada mostrando os
destaques/bilhetes ja calculados sem o texto da IA, em vez de derrubar
a pagina inteira.
"""
from unittest.mock import patch

import pytest
from google.genai.errors import APIError as GeminiAPIError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.campeonato import Campeonato
from app.models.time import Time
from app.models.partida import Partida
from app.routers.analise_ia import obter_analise
from app.services.analise_ia import IANaoConfiguradaError


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Sessao = sessionmaker(bind=engine)
    sessao = Sessao()
    yield sessao
    sessao.close()


@pytest.fixture
def partida_agendada(db):
    campeonato = Campeonato(
        nome="Brasileirão", pais_nome="Brasil", pais_codigo="BR",
        temporada=2026, temporada_label="2026", id_externo_liga=1,
    )
    db.add(campeonato)
    db.flush()

    mandante = Time(nome="Mandante", campeonato_id=campeonato.id, id_externo=1)
    visitante = Time(nome="Visitante", campeonato_id=campeonato.id, id_externo=2)
    db.add_all([mandante, visitante])
    db.flush()

    p = Partida(
        campeonato_id=campeonato.id,
        id_externo=999,
        status="agendada",
        time_mandante_id=mandante.id,
        time_visitante_id=visitante.id,
        rodada=1,
    )
    db.add(p)
    db.flush()
    return p


CALCULADO_FAKE = {
    "destaques_mandante": [],
    "destaques_visitante": [],
    "destaques_jogadores_mandante": [],
    "destaques_jogadores_visitante": [],
    "destaques_totais": [],
    "bilhete_simples": None,
    "bilhete_multipla": None,
}


def _erro_gemini_503():
    return GeminiAPIError(503, {"error": {"message": "This model is currently experiencing high demand."}})


def test_falha_transitoria_do_gemini_nao_derruba_a_rota(db, partida_agendada):
    with patch("app.routers.analise_ia._calcular_destaques_e_bilhetes", return_value=CALCULADO_FAKE), patch(
        "app.routers.analise_ia.gerar_analise", side_effect=_erro_gemini_503()
    ):
        resultado = obter_analise(partida_agendada.id, db)

    assert resultado.disponivel is False
    assert resultado.resumo is None
    assert resultado.dicas is None


def test_gemini_nao_configurado_continua_tratado_como_antes(db, partida_agendada):
    with patch("app.routers.analise_ia._calcular_destaques_e_bilhetes", return_value=CALCULADO_FAKE), patch(
        "app.routers.analise_ia.gerar_analise", side_effect=IANaoConfiguradaError()
    ):
        resultado = obter_analise(partida_agendada.id, db)

    assert resultado.disponivel is False
