"""
Testa scripts/enriquecer_sofascore.py contra um banco SQLite isolado em
memoria e respostas falsas do SofaScore -- cobre o comportamento
central: so' ENRIQUECE linhas ja existentes (criadas pelo pipeline da
Highlightly) com campos que ainda estao None, nunca sobrescreve valor
ja preenchido e nunca cria linha nova a partir do SofaScore sozinho.
"""
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.campeonato import Campeonato
from app.models.time import Time
from app.models.partida import Partida
from app.models.jogador import Jogador
from app.models.estatistica_jogador_partida import EstatisticaJogadorPartida
from scripts.enriquecer_sofascore import enriquecer_partida, casar_jogador, normalizar_nome


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Sessao = sessionmaker(bind=engine)
    sessao = Sessao()
    yield sessao
    sessao.close()


@pytest.fixture
def cenario(db):
    campeonato = Campeonato(
        nome="Brasileirão", pais_nome="Brasil", pais_codigo="BR",
        temporada=2026, temporada_label="2026", id_externo_liga=1,
    )
    db.add(campeonato)
    db.flush()

    mandante = Time(nome="Flamengo", campeonato_id=campeonato.id, id_externo=1001)
    visitante = Time(nome="Santos", campeonato_id=campeonato.id, id_externo=1002)
    db.add_all([mandante, visitante])
    db.flush()

    partida = Partida(
        campeonato_id=campeonato.id,
        id_externo=555,
        status="finalizada",
        time_mandante_id=mandante.id,
        time_visitante_id=visitante.id,
        gols_mandante=1,
        gols_visitante=0,
        rodada=1,
    )
    db.add(partida)
    db.flush()

    pedro = Jogador(id_externo=99, nome="Pedro", time_id=mandante.id)
    db.add(pedro)
    db.flush()

    stat_pedro = EstatisticaJogadorPartida(
        jogador_id=pedro.id, partida_id=partida.id, time_id=mandante.id, gols=1,
    )
    db.add(stat_pedro)
    db.commit()

    return partida, pedro, stat_pedro


LINEUPS_FAKE = {
    "home": {
        "players": [
            {
                "player": {"name": "Pedro Guilherme"},
                "statistics": {
                    "totalShots": 3,
                    "onTargetScoringAttempt": 2,
                    "fouls": 1,
                    "wasFouled": 2,
                    "minutesPlayed": 82,
                },
            },
            {
                "player": {"name": "Jogador Sem Match Nenhum"},
                "statistics": {"totalShots": 5},
            },
        ]
    },
    "away": {"players": []},
}


def test_enriquece_campos_ainda_nulos(db, cenario):
    partida, pedro, stat_pedro = cenario
    with patch("scripts.enriquecer_sofascore.buscar_lineups", return_value=LINEUPS_FAKE):
        atualizadas = enriquecer_partida(db, partida, {"id": 12345})

    assert atualizadas == 1
    db.refresh(stat_pedro)
    assert stat_pedro.chutes == 3
    assert stat_pedro.chutes_gol == 2
    assert stat_pedro.faltas_cometidas == 1
    assert stat_pedro.faltas_sofridas == 2
    assert stat_pedro.minutos_jogados == 82
    # gols veio da Highlightly, SofaScore nao mexe nele (nao faz parte do MAPA_CAMPOS)
    assert stat_pedro.gols == 1


def test_nao_sobrescreve_campo_ja_preenchido(db, cenario):
    partida, pedro, stat_pedro = cenario
    stat_pedro.chutes = 99  # ja preenchido por uma rodada anterior
    db.commit()

    with patch("scripts.enriquecer_sofascore.buscar_lineups", return_value=LINEUPS_FAKE):
        enriquecer_partida(db, partida, {"id": 12345})

    db.refresh(stat_pedro)
    assert stat_pedro.chutes == 99  # nao mudou
    assert stat_pedro.chutes_gol == 2  # esse sim estava None, foi preenchido


def test_jogador_sem_match_e_ignorado_sem_erro(db, cenario):
    partida, pedro, stat_pedro = cenario
    with patch("scripts.enriquecer_sofascore.buscar_lineups", return_value=LINEUPS_FAKE):
        enriquecer_partida(db, partida, {"id": 12345})

    # nao criou nenhuma linha nova pro "Jogador Sem Match Nenhum"
    assert db.query(Jogador).count() == 1
    assert db.query(EstatisticaJogadorPartida).count() == 1


def test_casar_jogador_por_nome_normalizado():
    j1 = Jogador(nome="Pedro", time_id=1)
    j2 = Jogador(nome="Léo Pereira", time_id=1)
    candidatos = [j1, j2]

    assert casar_jogador("Pedro Guilherme", candidatos) is j1
    assert casar_jogador("Leo Pereira", candidatos) is j2
    assert casar_jogador("Ninguem Conhecido", candidatos) is None


def test_normalizar_nome_remove_acento_e_ignora_maiuscula():
    assert normalizar_nome("Léo Pereira") == normalizar_nome("leo pereira")
