"""Testa a montagem da mensagem de anuncio de rodada contra um SQLite
isolado em memoria -- nao faz chamada real ao Telegram nem a Highlightly
(so' le o cache ja existente em AnaliseIAPartida.destaques_json)."""
import json
from datetime import date, time

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.campeonato import Campeonato  # noqa: F401
from app.models.time import Time
from app.models.partida import Partida
from app.models.analise_ia import AnaliseIAPartida
from scripts.anunciar_rodada import montar_mensagem_rodada, _frase_perna, _data_formatada


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Sessao = sessionmaker(bind=engine)
    sessao = Sessao()
    yield sessao
    sessao.close()


def _criar_partida_com_bilhete(db, mandante, visitante, rodada, dia, taxa, linha=2.5, tipo="quantidade", label="Chutes"):
    time_m = Time(nome=mandante, campeonato_id=1)
    time_v = Time(nome=visitante, campeonato_id=1)
    db.add_all([time_m, time_v])
    db.flush()

    partida = Partida(
        campeonato_id=1,
        status="agendada",
        rodada=rodada,
        data=dia,
        hora=time(18, 30),
        time_mandante_id=time_m.id,
        time_visitante_id=time_v.id,
    )
    db.add(partida)
    db.flush()

    destaque = {
        "stat": "chutes_a_favor",
        "label": label,
        "tipo": tipo,
        "linha": linha,
        "acertos": round(taxa * 10),
        "total": 10,
        "taxa": taxa,
        "sequencia": [1] * 10,
        "media": linha + 1,
    }
    perna = {"time": "mandante", "nome_time": mandante, "destaque": destaque}
    calculado = {
        "destaques_mandante": [],
        "destaques_visitante": [],
        "destaques_jogadores_mandante": [],
        "destaques_jogadores_visitante": [],
        "destaques_totais": [],
        "bilhete_simples": {"perna": perna, "confianca": min(taxa, 0.8) * 10},
        "bilhete_multipla": None,
    }
    db.add(
        AnaliseIAPartida(
            partida_id=partida.id,
            texto="resumo fake",
            dicas=None,
            modelo="fake",
            destaques_json=json.dumps(calculado),
        )
    )
    db.commit()
    return partida


def test_escolhe_o_bilhete_de_maior_confianca_como_destaque(db):
    _criar_partida_com_bilhete(db, "Flamengo", "Botafogo", rodada=25, dia=date(2026, 8, 29), taxa=0.7)
    partida_melhor = _criar_partida_com_bilhete(db, "Palmeiras", "Corinthians", rodada=25, dia=date(2026, 8, 30), taxa=0.9)

    texto = montar_mensagem_rodada(db, campeonato_id=1, numero_rodada=25)

    assert "Palmeiras x Corinthians" in texto
    assert f"/analise/{partida_melhor.id}" in texto
    assert "Flamengo x Botafogo" not in texto.split("Melhor palpite")[1].split("\n")[0]


def test_menciona_quantidade_de_jogos_restantes_no_plural(db):
    _criar_partida_com_bilhete(db, "Flamengo", "Botafogo", rodada=25, dia=date(2026, 8, 29), taxa=0.9)
    _criar_partida_com_bilhete(db, "Palmeiras", "Corinthians", rodada=25, dia=date(2026, 8, 30), taxa=0.7)

    texto = montar_mensagem_rodada(db, campeonato_id=1, numero_rodada=25)

    assert "Mais 1 jogo com" in texto  # singular correto pro 1 jogo restante


def test_rodada_sem_partida_agendada_devolve_none(db):
    assert montar_mensagem_rodada(db, campeonato_id=1, numero_rodada=99) is None


def test_frase_perna_quantidade():
    perna = {
        "time": "visitante",
        "nome_time": "Athletico-PR",
        "destaque": {"tipo": "quantidade", "linha": 18.5, "label": "Chutes totais"},
    }
    assert _frase_perna(perna) == "Athletico-PR fora de casa tende a passar de 18.5 chutes totais"


def test_frase_perna_booleano():
    perna = {
        "time": "mandante",
        "nome_time": "Flamengo",
        "destaque": {"tipo": "booleano", "linha": 0.5, "label": "Não perde"},
    }
    assert _frase_perna(perna) == "Flamengo em casa: não perde"


def test_data_formatada_com_hora():
    partida = Partida(data=date(2026, 8, 29), hora=time(18, 30))
    assert _data_formatada(partida) == "sábado, 29/08 às 18h30"


def test_data_formatada_sem_data():
    partida = Partida(data=None, hora=None)
    assert _data_formatada(partida) == ""
