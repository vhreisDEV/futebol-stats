"""
Testa app/services/jogadores.py::obter_grade_time -- a grade estilo
PlayerStats.com (colunas = ultimos N jogos do time, linhas = jogadores).
Cobre o comportamento central: jogo que o jogador nao jogou fica com
valor None (nao 0), jogadores sao buscados pela propria linha de
estatistica daquele jogo+time (nao pelo time ATUAL do jogador -- mesma
licao do bug real corrigido em enriquecer_sofascore.py pra quem foi
transferido depois), e "defesas" so' traz goleiro.
"""
from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.campeonato import Campeonato
from app.models.time import Time
from app.models.jogador import Jogador
from app.models.partida import Partida
from app.models.estatistica_jogador_partida import EstatisticaJogadorPartida
from app.services.jogadores import obter_grade_time


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

    time = Time(nome="Meu Time", campeonato_id=campeonato.id, id_externo=1)
    adversario1 = Time(nome="Adversario 1", campeonato_id=campeonato.id, id_externo=2)
    adversario2 = Time(nome="Adversario 2", campeonato_id=campeonato.id, id_externo=3)
    db.add_all([time, adversario1, adversario2])
    db.flush()

    p1 = Partida(
        campeonato_id=campeonato.id, id_externo=101, status="finalizada", rodada=1,
        time_mandante_id=time.id, time_visitante_id=adversario1.id,
        gols_mandante=2, gols_visitante=1, data=date(2026, 1, 10),
    )
    p2 = Partida(
        campeonato_id=campeonato.id, id_externo=102, status="finalizada", rodada=2,
        time_mandante_id=adversario2.id, time_visitante_id=time.id,
        gols_mandante=0, gols_visitante=0, data=date(2026, 1, 17),
    )
    db.add_all([p1, p2])
    db.flush()

    titular = Jogador(nome="Titular", posicao="Defensor", time_id=time.id)
    reserva = Jogador(nome="Reserva", posicao="Meia", time_id=time.id)
    goleiro = Jogador(nome="Goleiro Um", posicao="Goleiro", time_id=time.id)
    db.add_all([titular, reserva, goleiro])
    db.flush()

    # Titular jogou os dois jogos, Reserva so' o segundo (o primeiro fica
    # None pra ele -- nao foi relacionado, nao e' "jogou e fez zero").
    db.add_all([
        EstatisticaJogadorPartida(jogador_id=titular.id, partida_id=p1.id, time_id=time.id, desarmes=3),
        EstatisticaJogadorPartida(jogador_id=titular.id, partida_id=p2.id, time_id=time.id, desarmes=5),
        EstatisticaJogadorPartida(jogador_id=reserva.id, partida_id=p2.id, time_id=time.id, desarmes=1),
        EstatisticaJogadorPartida(jogador_id=goleiro.id, partida_id=p1.id, time_id=time.id, defesas=4),
        EstatisticaJogadorPartida(jogador_id=goleiro.id, partida_id=p2.id, time_id=time.id, defesas=2),
    ])
    db.commit()

    return {"time": time, "p1": p1, "p2": p2, "titular": titular, "reserva": reserva, "goleiro": goleiro}


def test_jogo_nao_jogado_fica_com_valor_none(db, cenario):
    grade = obter_grade_time(db, cenario["time"].id, "desarmes", quantidade=10)

    assert len(grade["jogos"]) == 2
    reserva = next(j for j in grade["jogadores"] if j["nome"] == "Reserva")
    # jogos ordenados do mais recente pro mais antigo -> p2 primeiro, p1 depois
    assert reserva["valores"] == [1, None]
    assert reserva["total"] == 1
    assert reserva["media"] == 1.0  # media so conta jogo com valor real, nao conta o None


def test_ordenado_por_total_decrescente(db, cenario):
    grade = obter_grade_time(db, cenario["time"].id, "desarmes", quantidade=10)
    nomes = [j["nome"] for j in grade["jogadores"]]
    # Titular tem 8 desarmes, Reserva tem 1, Goleiro Um aparece tambem
    # (tem linha de estatistica nos 2 jogos, so' que sem valor de
    # desarmes registrado -- total 0, fica por ultimo)
    assert nomes == ["Titular", "Reserva", "Goleiro Um"]


def test_defesas_so_traz_goleiro(db, cenario):
    grade = obter_grade_time(db, cenario["time"].id, "defesas", quantidade=10)
    nomes = [j["nome"] for j in grade["jogadores"]]
    assert nomes == ["Goleiro Um"]


def test_filtro_mando_casa(db, cenario):
    # Meu Time so' jogou em casa na p1 (mandante) -- filtrar "casa" deve
    # trazer so' esse jogo.
    grade = obter_grade_time(db, cenario["time"].id, "desarmes", quantidade=10, mando="casa")
    assert len(grade["jogos"]) == 1
    assert grade["jogos"][0]["partida_id"] == cenario["p1"].id
    assert grade["jogos"][0]["casa_ou_fora"] == "casa"
    assert grade["jogos"][0]["placar"] == "2-1"


def test_jogador_encontrado_pela_linha_da_partida_nao_pelo_time_atual(db, cenario):
    # Regressao da mesma licao do bug real do enriquecimento SofaScore:
    # jogador ja transferido (Jogador.time_id mudou) ainda deve aparecer
    # na grade do time antigo, porque a linha de estatistica da partida
    # antiga (EstatisticaJogadorPartida.time_id) e' o que importa.
    cenario["titular"].time_id = 999  # "transferido"
    db.commit()

    grade = obter_grade_time(db, cenario["time"].id, "desarmes", quantidade=10)
    nomes = [j["nome"] for j in grade["jogadores"]]
    assert "Titular" in nomes


def test_stat_invalido_devolve_none(db, cenario):
    assert obter_grade_time(db, cenario["time"].id, "stat_que_nao_existe") is None
