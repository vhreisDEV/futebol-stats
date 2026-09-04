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
from scripts.enriquecer_sofascore import enriquecer_partida, casar_jogador, normalizar_nome, encontrar_evento, CONFIG_LIGA


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


def test_stat_ausente_vira_zero_quando_jogador_jogou(db, cenario):
    # Regressao do bug real encontrado 2026-09-03: o SofaScore omite a
    # chave inteira da estatistica quando o valor real e' 0 (Luan Peres
    # jogou 90min contra o Vasco e tinha "totalTackle" ausente do
    # payload -- 0 desarmes de verdade, nao dado faltando). Sem essa
    # regra o campo ficava None pra sempre e a celula da grade parecia
    # "nao jogou" quando na verdade ele jogou e so nao fez aquele stat.
    partida, pedro, stat_pedro = cenario
    lineups_sem_desarme = {
        "home": {
            "players": [
                {
                    "player": {"name": "Pedro Guilherme"},
                    "statistics": {"minutesPlayed": 90, "totalShots": 1},
                    # sem "totalTackle", "fouls", "wasFouled", "saves" -- todos zero de verdade
                },
            ]
        },
        "away": {"players": []},
    }
    with patch("scripts.enriquecer_sofascore.buscar_lineups", return_value=lineups_sem_desarme):
        enriquecer_partida(db, partida, {"id": 12345})

    db.refresh(stat_pedro)
    assert stat_pedro.chutes == 1
    assert stat_pedro.desarmes == 0
    assert stat_pedro.faltas_cometidas == 0
    assert stat_pedro.faltas_sofridas == 0
    assert stat_pedro.minutos_jogados == 90


def test_stat_ausente_continua_none_quando_jogador_nao_jogou(db, cenario):
    # Contraste do teste acima: sem "minutesPlayed" (reserva nao
    # utilizado), ausencia de chave nao significa nada -- continua None,
    # tratado como "nao jogou" no frontend.
    partida, pedro, stat_pedro = cenario
    lineups_banco = {
        "home": {
            "players": [
                {"player": {"name": "Pedro Guilherme"}, "statistics": {"totalShots": 0}},
            ]
        },
        "away": {"players": []},
    }
    with patch("scripts.enriquecer_sofascore.buscar_lineups", return_value=lineups_banco):
        enriquecer_partida(db, partida, {"id": 12345})

    db.refresh(stat_pedro)
    assert stat_pedro.desarmes is None
    assert stat_pedro.minutos_jogados is None


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


def test_casar_jogador_prefere_match_exato_sobre_parcial_empatado():
    # Regressao do bug real encontrado 2026-09-02: dois jogadores reais
    # do Bahia, "Erick" e "Erick Pulga", empatavam no score de
    # intersecao de tokens contra o nome "Erick" vindo do SofaScore
    # (ambos batem 1 token: "erick") -- sem preferir o match exato, o
    # "Erick" ficava as vezes sem ser enriquecido (o "Erick Pulga"
    # ganhava o empate por ordem arbitraria).
    erick = Jogador(nome="Erick", time_id=1)
    erick_pulga = Jogador(nome="Erick Pulga", time_id=1)
    candidatos = [erick_pulga, erick]  # Erick Pulga listado primeiro de proposito

    assert casar_jogador("Erick", candidatos) is erick
    assert casar_jogador("Erick Pulga", candidatos) is erick_pulga


def test_casar_jogador_devolve_none_em_empate_parcial_ambiguo():
    # Sem nome exato batendo e o melhor score parcial empatado entre
    # 2+ candidatos diferentes -- melhor nao adivinhar.
    a = Jogador(nome="João Silva Santos", time_id=1)
    b = Jogador(nome="Pedro Silva Costa", time_id=1)
    assert casar_jogador("Silva", [a, b]) is None


def test_normalizar_nome_remove_acento_e_ignora_maiuscula():
    assert normalizar_nome("Léo Pereira") == normalizar_nome("leo pereira")


def test_enriquece_jogador_ja_transferido_pra_outro_time(db, cenario):
    # Regressao do bug real encontrado 2026-09-02: um goleiro jogava no
    # Bahia na rodada 16, foi transferido pro Chapecoense depois --
    # Jogador.time_id ja reflete o time NOVO (upsert_jogador sempre
    # sobrescreve pelo time da partida mais recente processada). Antes,
    # o enriquecimento buscava candidatos por Jogador.time_id == time da
    # partida antiga, entao o jogador nunca aparecia no "elenco" do time
    # antigo mesmo tendo uma linha de estatistica real pra essa partida.
    # Agora busca por quem JA TEM linha nessa partida por esse time.
    partida, pedro, stat_pedro = cenario
    pedro.time_id = 999  # "transferido" pro Chapecoense (id fake), depois da partida
    db.commit()

    with patch("scripts.enriquecer_sofascore.buscar_lineups", return_value=LINEUPS_FAKE):
        atualizadas = enriquecer_partida(db, partida, {"id": 12345})

    assert atualizadas == 1
    db.refresh(stat_pedro)
    assert stat_pedro.chutes == 3


def test_config_liga_nao_tem_id_sofascore_duplicado_dentro_da_liga():
    # Sanity check pra evitar erro de copia-e-cola ao adicionar uma liga
    # nova em CONFIG_LIGA: dois times da MESMA liga apontando pro mesmo
    # id do SofaScore faria o encontrar_evento/casar_jogador confundir
    # os dois silenciosamente.
    for campeonato_id, config in CONFIG_LIGA.items():
        ids_sofascore = list(config["times"].values())
        assert len(ids_sofascore) == len(set(ids_sofascore)), (
            f"campeonato_id={campeonato_id} tem id de time do SofaScore duplicado"
        )


def test_encontrar_evento_prefere_finalizado_sobre_adiado(cenario):
    # Regressao do bug real encontrado 2026-09-02: uma partida
    # adiada/remarcada aparece DUAS vezes na listagem da rodada do
    # SofaScore -- o evento adiado original (sem lineup) e o jogo de
    # verdade jogado depois. Sem preferir o "finished", o adiado (que
    # normalmente vem primeiro na lista) ganhava e a partida ficava sem
    # nenhum jogador enriquecido.
    partida, _, _ = cenario
    mapa_fake = {partida.time_mandante_id: 1001, partida.time_visitante_id: 1002}
    eventos_rodada = [
        {"homeTeam": {"id": 1001}, "awayTeam": {"id": 1002}, "id": 111, "status": {"type": "postponed", "description": "Postponed"}},
        {"homeTeam": {"id": 1001}, "awayTeam": {"id": 1002}, "id": 222, "status": {"type": "finished", "description": "Ended"}},
    ]
    evento = encontrar_evento(partida, eventos_rodada, mapa_fake)
    assert evento["id"] == 222
