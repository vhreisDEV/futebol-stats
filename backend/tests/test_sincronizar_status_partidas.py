"""
Testa scripts/sincronizar_status_partidas.py::sincronizar_liga contra um
banco SQLite isolado em memoria -- cobre o bug real encontrado
2026-08-26: partidas de outras ligas (La Liga) ficando presas como
"agendada" mesmo com data ja passada, porque importar_partidas.py so
roda liga por liga e a cota costuma se esgotar antes de chegar nelas.
Essa sincronizacao so' atualiza status/placar/data (nunca estatisticas),
entao os testes cobrem: criar partida nova, atualizar status existente,
e NUNCA sobrescrever uma partida ja enriquecida com estatisticas
completas.
"""
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.campeonato import Campeonato
from app.models.time import Time
from app.models.partida import Partida
from scripts.sincronizar_status_partidas import sincronizar_liga


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Sessao = sessionmaker(bind=engine)
    sessao = Sessao()
    yield sessao
    sessao.close()


@pytest.fixture
def campeonato(db):
    c = Campeonato(
        nome="La Liga",
        pais_nome="Spain",
        pais_codigo="ES",
        temporada=2026,
        temporada_label="2026-27",
        id_externo_liga=999,
    )
    db.add(c)
    db.flush()
    return c


@pytest.fixture
def times(db, campeonato):
    mandante = Time(nome="Mandante", campeonato_id=campeonato.id, id_externo=101)
    visitante = Time(nome="Visitante", campeonato_id=campeonato.id, id_externo=102)
    db.add_all([mandante, visitante])
    db.flush()
    return mandante, visitante


def _match(id_externo, estado, rodada=1, score=None, dia="2026-08-24T22:30:00.000Z"):
    return {
        "id": id_externo,
        "homeTeam": {"id": 101, "name": "Mandante"},
        "awayTeam": {"id": 102, "name": "Visitante"},
        "state": {"description": estado, "score": {"current": score} if score else {}},
        "round": f"Regular Season - {rodada}",
        "date": dia,
    }


def test_cria_partida_nova_agendada(db, campeonato, times):
    matches = [_match(5001, "Not Started", rodada=2)]
    with patch("scripts.sincronizar_status_partidas.buscar_temporada_completa", return_value=matches):
        criadas, atualizadas, sem_mudanca = sincronizar_liga(db, campeonato)

    assert (criadas, atualizadas, sem_mudanca) == (1, 0, 0)
    partida = db.query(Partida).filter(Partida.id_externo == 5001).first()
    assert partida.status == "agendada"
    assert partida.rodada == 2


def test_atualiza_status_de_agendada_pra_finalizada_sem_pedir_estatisticas(db, campeonato, times):
    # Partida ja existia como "agendada" (data passada, cenario real do
    # bug) -- a sincronizacao deve virar "finalizada" com o placar certo,
    # sem NUNCA chamar nenhuma rota de estatisticas.
    partida = Partida(
        id_externo=5002,
        campeonato_id=campeonato.id,
        time_mandante_id=times[0].id,
        time_visitante_id=times[1].id,
        status="agendada",
        rodada=1,
    )
    db.add(partida)
    db.flush()

    matches = [_match(5002, "Full-time", rodada=1, score="2 - 1")]
    with patch("scripts.sincronizar_status_partidas.buscar_temporada_completa", return_value=matches):
        criadas, atualizadas, sem_mudanca = sincronizar_liga(db, campeonato)

    assert (criadas, atualizadas, sem_mudanca) == (0, 1, 0)
    db.refresh(partida)
    assert partida.status == "finalizada"
    assert (partida.gols_mandante, partida.gols_visitante) == (2, 1)
    assert partida.escanteios_mandante is None  # estatisticas ficam pra importar_partidas.py depois


def test_nao_sobrescreve_partida_ja_enriquecida_com_estatisticas(db, campeonato, times):
    # Partida ja tem estatisticas completas -- mesmo que o placar da API
    # divirja (nao deveria acontecer, mas por seguranca), o script so'
    # avisa e nao mexe em nada.
    partida = Partida(
        id_externo=5003,
        campeonato_id=campeonato.id,
        time_mandante_id=times[0].id,
        time_visitante_id=times[1].id,
        status="finalizada",
        gols_mandante=3,
        gols_visitante=0,
        rodada=1,
        escanteios_mandante=5,
        escanteios_visitante=2,
    )
    db.add(partida)
    db.flush()

    matches = [_match(5003, "Full-time", rodada=1, score="3 - 0")]
    with patch("scripts.sincronizar_status_partidas.buscar_temporada_completa", return_value=matches):
        criadas, atualizadas, sem_mudanca = sincronizar_liga(db, campeonato)

    assert (criadas, atualizadas, sem_mudanca) == (0, 0, 1)
    db.refresh(partida)
    assert (partida.gols_mandante, partida.gols_visitante) == (3, 0)


def test_pula_partida_de_time_nao_cadastrado(db, campeonato):
    matches = [_match(5004, "Not Started", rodada=1)]
    with patch("scripts.sincronizar_status_partidas.buscar_temporada_completa", return_value=matches):
        criadas, atualizadas, sem_mudanca = sincronizar_liga(db, campeonato)

    assert (criadas, atualizadas, sem_mudanca) == (0, 0, 0)
    assert db.query(Partida).count() == 0
