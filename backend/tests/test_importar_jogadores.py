"""
Testa scripts/importar_jogadores.py::processar_partida contra um banco
SQLite isolado em memoria (nunca toca no banco de dev real) e eventos
falsos da Highlightly -- cobre exatamente a classe de bug encontrada
2026-08-25: gol de penalti (type="Penalty") nao sendo creditado ao
jogador porque so "Goal" era somado. Gol contra (type="Own Goal") e'
verificado como intencionalmente NAO contando pro jogador (convencao de
estatistica de futebol), nao um bug.
"""
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.campeonato import Campeonato  # noqa: F401 -- precisa estar registrado pro FK de Time/Partida resolver
from app.models.time import Time
from app.models.partida import Partida
from app.models.jogador import Jogador
from app.models.estatistica_jogador_partida import EstatisticaJogadorPartida
from scripts.importar_jogadores import processar_partida


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Sessao = sessionmaker(bind=engine)
    sessao = Sessao()
    yield sessao
    sessao.close()


@pytest.fixture
def partida(db):
    mandante = Time(nome="Time Mandante", campeonato_id=1, id_externo=1001)
    visitante = Time(nome="Time Visitante", campeonato_id=1, id_externo=1002)
    db.add_all([mandante, visitante])
    db.flush()

    p = Partida(
        campeonato_id=1,
        id_externo=555,
        status="finalizada",
        time_mandante_id=mandante.id,
        time_visitante_id=visitante.id,
        gols_mandante=2,
        gols_visitante=1,
        rodada=1,
    )
    db.add(p)
    db.flush()
    return p


LINEUPS_FAKE = {
    "homeTeam": {
        "initialLineup": [[{"id": 10, "name": "Artilheiro", "position": "Forward"}]],
        "substitutes": [{"id": 12, "name": "Reserva", "position": "Midfielder"}],
    },
    "awayTeam": {
        "initialLineup": [[{"id": 20, "name": "Zagueiro Contra", "position": "Defender"}]],
        "substitutes": [],
    },
}


def _evento(team_id_externo, tipo, player_id, player_nome, minuto="10", assist_id=None, assist_nome=None, substituted=None):
    return {
        "team": {"id": team_id_externo},
        "time": minuto,
        "type": tipo,
        "player": player_nome,
        "playerId": player_id,
        "assist": assist_nome,
        "assistingPlayerId": assist_id,
        "substituted": substituted,
    }


def test_gol_de_penalti_e_creditado_ao_jogador(db, partida):
    # Regressao do bug real encontrado 2026-08-25: Highlightly marca
    # penalti convertido como type="Penalty", nao "Goal".
    events = [_evento(1001, "Penalty", 10, "Artilheiro", minuto="27")]

    with patch("scripts.importar_jogadores.buscar_lineups", return_value=LINEUPS_FAKE), patch(
        "scripts.importar_jogadores.buscar_events", return_value=events
    ):
        novas, erro = processar_partida(db, partida, cache_jogadores={})

    assert erro is None
    jogador = db.query(Jogador).filter(Jogador.id_externo == 10).first()
    linha = db.query(EstatisticaJogadorPartida).filter_by(jogador_id=jogador.id, partida_id=partida.id).first()
    assert linha.gols == 1


def test_gol_normal_e_creditado_ao_jogador(db, partida):
    events = [_evento(1001, "Goal", 10, "Artilheiro", minuto="10")]

    with patch("scripts.importar_jogadores.buscar_lineups", return_value=LINEUPS_FAKE), patch(
        "scripts.importar_jogadores.buscar_events", return_value=events
    ):
        processar_partida(db, partida, cache_jogadores={})

    jogador = db.query(Jogador).filter(Jogador.id_externo == 10).first()
    linha = db.query(EstatisticaJogadorPartida).filter_by(jogador_id=jogador.id, partida_id=partida.id).first()
    assert linha.gols == 1


def test_gol_contra_nao_e_creditado_ao_proprio_jogador(db, partida):
    # Por convencao de estatistica de futebol, gol contra NAO conta como
    # gol do jogador que fez contra -- isso e' intencional, nao um bug.
    events = [_evento(1002, "Own Goal", 20, "Zagueiro Contra", minuto="62")]

    with patch("scripts.importar_jogadores.buscar_lineups", return_value=LINEUPS_FAKE), patch(
        "scripts.importar_jogadores.buscar_events", return_value=events
    ):
        processar_partida(db, partida, cache_jogadores={})

    jogador = db.query(Jogador).filter(Jogador.id_externo == 20).first()
    linha = db.query(EstatisticaJogadorPartida).filter_by(jogador_id=jogador.id, partida_id=partida.id).first()
    assert linha.gols == 0


def test_assistencia_de_penalti_nao_existe_mas_de_gol_normal_e_creditada(db, partida):
    events = [_evento(1001, "Goal", 10, "Artilheiro", minuto="10", assist_id=12, assist_nome="Reserva")]

    with patch("scripts.importar_jogadores.buscar_lineups", return_value=LINEUPS_FAKE), patch(
        "scripts.importar_jogadores.buscar_events", return_value=events
    ):
        processar_partida(db, partida, cache_jogadores={})

    assistente = db.query(Jogador).filter(Jogador.id_externo == 12).first()
    linha = db.query(EstatisticaJogadorPartida).filter_by(jogador_id=assistente.id, partida_id=partida.id).first()
    assert linha.assistencias == 1


def test_cartao_amarelo_e_creditado(db, partida):
    events = [_evento(1001, "Yellow Card", 10, "Artilheiro", minuto="30")]

    with patch("scripts.importar_jogadores.buscar_lineups", return_value=LINEUPS_FAKE), patch(
        "scripts.importar_jogadores.buscar_events", return_value=events
    ):
        processar_partida(db, partida, cache_jogadores={})

    jogador = db.query(Jogador).filter(Jogador.id_externo == 10).first()
    linha = db.query(EstatisticaJogadorPartida).filter_by(jogador_id=jogador.id, partida_id=partida.id).first()
    assert linha.cartoes_amarelos == 1


def test_jogador_que_saiu_na_substituicao_tambem_e_registrado(db, partida):
    # Regressao do bug real encontrado 2026-08-26: o Pedro (Flamengo)
    # sumia do banco inteiro porque o /lineups da Highlightly errou pra
    # essa partida e o listou como reserva (nunca aparecia no
    # initialLineup), e o import so registrava quem ENTRAVA na
    # substituicao, nunca quem saia -- mesmo o /events confirmando que
    # ele jogou (foi substituido aos 46min). "assistingPlayerId"/
    # "substituted" no evento de substituicao carregam o id/nome de quem
    # saiu (confirmado comparando com o id_externo real do Pedro ja
    # salvo no banco).
    events = [
        _evento(1001, "Substitution", 999, "Entrou", minuto="46", assist_id=888, substituted="Saiu"),
    ]

    with patch("scripts.importar_jogadores.buscar_lineups", return_value=LINEUPS_FAKE), patch(
        "scripts.importar_jogadores.buscar_events", return_value=events
    ):
        processar_partida(db, partida, cache_jogadores={})

    saiu = db.query(Jogador).filter(Jogador.id_externo == 888).first()
    assert saiu is not None
    assert saiu.nome == "Saiu"
    linha_saiu = db.query(EstatisticaJogadorPartida).filter_by(jogador_id=saiu.id, partida_id=partida.id).first()
    assert linha_saiu is not None

    entrou = db.query(Jogador).filter(Jogador.id_externo == 999).first()
    assert entrou is not None
    linha_entrou = db.query(EstatisticaJogadorPartida).filter_by(jogador_id=entrou.id, partida_id=partida.id).first()
    assert linha_entrou is not None


def test_titular_sem_nenhum_evento_ainda_conta_como_aparicao(db, partida):
    # Titulares entram com "0 de tudo" so' pelo lineup -- garante que a
    # contagem de "jogos" do jogador fica certa mesmo sem contribuicao.
    events = []

    with patch("scripts.importar_jogadores.buscar_lineups", return_value=LINEUPS_FAKE), patch(
        "scripts.importar_jogadores.buscar_events", return_value=events
    ):
        processar_partida(db, partida, cache_jogadores={})

    jogador = db.query(Jogador).filter(Jogador.id_externo == 10).first()
    linha = db.query(EstatisticaJogadorPartida).filter_by(jogador_id=jogador.id, partida_id=partida.id).first()
    assert linha is not None
    assert linha.gols == 0
