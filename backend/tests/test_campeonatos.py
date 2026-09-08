"""
Testa app/routers/campeonatos.py::_jogos_minimo_por_time -- regressao do
bug real encontrado 2026-09-08: a La Liga tinha rodada_atual=6 (MAX das
rodadas finalizadas), mas isso vinha de UMA UNICA partida remarcada pra
rodada 6 (Celta de Vigo x Real Sociedad) -- os outros 18 times ainda
so tinham 4 jogos. rodada_atual sozinho fazia RODADA_MINIMA_FUNCOES_
AVANCADAS liberar Previsao/Dicas/Comparar com dado de menos jogos do
que o esperado pra quase todo mundo.
"""
from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.campeonato import Campeonato
from app.models.time import Time
from app.models.partida import Partida
from app.routers.campeonatos import _jogos_minimo_por_time


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Sessao = sessionmaker(bind=engine)
    sessao = Sessao()
    yield sessao
    sessao.close()


def _campeonato(db):
    campeonato = Campeonato(
        nome="La Liga", pais_nome="Espanha", pais_codigo="ES",
        temporada=2026, temporada_label="26/27", id_externo_liga=1,
    )
    db.add(campeonato)
    db.flush()
    return campeonato


def _partida(db, campeonato, rodada, mandante, visitante, status="finalizada", id_externo=None):
    p = Partida(
        campeonato_id=campeonato.id, id_externo=id_externo or (rodada * 1000 + mandante.id),
        status=status, rodada=rodada, time_mandante_id=mandante.id, time_visitante_id=visitante.id,
        gols_mandante=1, gols_visitante=0, data=date(2026, 8, rodada),
    )
    db.add(p)
    return p


def test_uma_partida_remarcada_nao_infla_o_minimo(db):
    # Regressao exata do bug real: 4 times, 3 jogaram so 1 rodada cada
    # (1 jogo), mas 2 deles (B e C) tambem se enfrentam numa rodada
    # futura remarcada (rodada 5) -- MAX(rodada) reportaria 5, mas o
    # minimo de jogos entre os 4 times continua sendo 1.
    campeonato = _campeonato(db)
    a = Time(nome="A", campeonato_id=campeonato.id, id_externo=1)
    b = Time(nome="B", campeonato_id=campeonato.id, id_externo=2)
    c = Time(nome="C", campeonato_id=campeonato.id, id_externo=3)
    d = Time(nome="D", campeonato_id=campeonato.id, id_externo=4)
    db.add_all([a, b, c, d])
    db.flush()

    _partida(db, campeonato, rodada=1, mandante=a, visitante=d)
    _partida(db, campeonato, rodada=1, mandante=b, visitante=c, id_externo=9999)
    _partida(db, campeonato, rodada=5, mandante=b, visitante=c, id_externo=9998)
    db.commit()

    assert _jogos_minimo_por_time(db, campeonato.id) == 1


def test_todos_com_o_mesmo_numero_de_jogos(db):
    campeonato = _campeonato(db)
    times = [Time(nome=f"Time {i}", campeonato_id=campeonato.id, id_externo=i) for i in range(1, 5)]
    db.add_all(times)
    db.flush()
    a, b, c, d = times

    _partida(db, campeonato, rodada=1, mandante=a, visitante=b)
    _partida(db, campeonato, rodada=1, mandante=c, visitante=d, id_externo=9999)
    _partida(db, campeonato, rodada=2, mandante=a, visitante=c, id_externo=9998)
    _partida(db, campeonato, rodada=2, mandante=b, visitante=d, id_externo=9997)
    db.commit()

    assert _jogos_minimo_por_time(db, campeonato.id) == 2


def test_ignora_partidas_agendadas_e_adiadas(db):
    campeonato = _campeonato(db)
    a = Time(nome="A", campeonato_id=campeonato.id, id_externo=1)
    b = Time(nome="B", campeonato_id=campeonato.id, id_externo=2)
    db.add_all([a, b])
    db.flush()

    _partida(db, campeonato, rodada=1, mandante=a, visitante=b, status="finalizada")
    _partida(db, campeonato, rodada=2, mandante=a, visitante=b, status="agendada", id_externo=9999)
    _partida(db, campeonato, rodada=3, mandante=a, visitante=b, status="adiada", id_externo=9998)
    db.commit()

    assert _jogos_minimo_por_time(db, campeonato.id) == 1


def test_campeonato_sem_time_devolve_none(db):
    campeonato = _campeonato(db)
    db.commit()

    assert _jogos_minimo_por_time(db, campeonato.id) is None


def test_time_sem_nenhuma_partida_conta_zero(db):
    campeonato = _campeonato(db)
    a = Time(nome="A", campeonato_id=campeonato.id, id_externo=1)
    b = Time(nome="B", campeonato_id=campeonato.id, id_externo=2)
    sem_jogo = Time(nome="Sem jogo ainda", campeonato_id=campeonato.id, id_externo=3)
    db.add_all([a, b, sem_jogo])
    db.flush()

    _partida(db, campeonato, rodada=1, mandante=a, visitante=b)
    db.commit()

    assert _jogos_minimo_por_time(db, campeonato.id) == 0
