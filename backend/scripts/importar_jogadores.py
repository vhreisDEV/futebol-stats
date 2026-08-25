# -*- coding: utf-8 -*-
"""
Importa dado real de jogador (gols, assistencias, cartoes) via
/lineups/{id} + /events/{id} da Highlightly. Confirmado 2026-08-19: a
API so da isso por jogador -- chutes/chutes ao gol/desarmes/faltas so
existem em nivel de time (/statistics), nao tem como preencher esses
campos com dado real por enquanto (ficam None, igual sempre foi tratado
nesse projeto pra dado ausente).

2 chamadas por partida (lineups + events), contra 1 chamada de
/statistics que o importar_partidas.py ja faz -- backfill completo do
historico (todas as partidas finalizadas) nao cabe num dia so de cota,
precisa rodar em varios dias.

Uso (de dentro de backend/, local usa SQLite; pra produção, ver
importar_jogadores_producao.py):
    py scripts/importar_jogadores.py
"""
import os
import sys

import requests
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.time import Time
from app.models.partida import Partida
from app.models.jogador import Jogador
from app.models.estatistica_jogador_partida import EstatisticaJogadorPartida

load_dotenv()

API_KEY = os.getenv("HIGHLIGHTLY_API_KEY")
BASE_URL = "https://soccer.highlightly.net"
HEADERS = {"x-rapidapi-key": API_KEY}

MAX_PARTIDAS_POR_EXECUCAO = 40  # 2 chamadas cada (lineups + events) -- ~80 requests, com folga da cota de 100/dia

POSICAO_PT = {
    "Goalkeeper": "Goleiro",
    "Defender": "Zagueiro",
    "Midfielder": "Meia",
    "Forward": "Atacante",
}


class CotaExcedidaError(Exception):
    pass


def _get(url):
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 429:
        raise CotaExcedidaError()
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()


def buscar_lineups(match_id):
    return _get(f"{BASE_URL}/lineups/{match_id}")


def buscar_events(match_id):
    return _get(f"{BASE_URL}/events/{match_id}")


def upsert_jogador(db, cache, id_externo, nome, posicao_en, time_id):
    if id_externo in cache:
        return cache[id_externo]

    jogador = db.query(Jogador).filter(Jogador.id_externo == id_externo).first()
    posicao = POSICAO_PT.get(posicao_en, posicao_en)

    if jogador:
        jogador.nome = nome
        if posicao:
            jogador.posicao = posicao
        jogador.time_id = time_id
    else:
        jogador = Jogador(id_externo=id_externo, nome=nome, posicao=posicao, time_id=time_id)
        db.add(jogador)
        db.flush()

    cache[id_externo] = jogador
    return jogador


def processar_partida(db, partida, cache_jogadores):
    lineups = buscar_lineups(partida.id_externo)
    events = buscar_events(partida.id_externo)
    if lineups is None or events is None:
        return 0, "sem lineups ou events disponiveis pra essa partida"

    time_mandante = db.query(Time).filter(Time.id == partida.time_mandante_id).first()
    time_visitante = db.query(Time).filter(Time.id == partida.time_visitante_id).first()

    mapa_times = {
        time_mandante.id_externo: time_mandante.id,
        time_visitante.id_externo: time_visitante.id,
    }
    mapa_bloco = {
        time_mandante.id_externo: lineups.get("homeTeam", {}),
        time_visitante.id_externo: lineups.get("awayTeam", {}),
    }

    # nome/posicao conhecidos de cada jogador (titular ou reserva) pelos
    # lineups -- o /events so da id e nome, nunca posicao.
    info_jogadores = {}
    for time_id_externo, bloco in mapa_bloco.items():
        for linha in bloco.get("initialLineup", []):
            for j in linha:
                info_jogadores[j["id"]] = (j["name"], j["position"])
        for s in bloco.get("substitutes", []):
            info_jogadores.setdefault(s["id"], (s["name"], s["position"]))

    estatisticas = {}

    def registrar(player_id, nome_fallback, time_id_externo):
        time_id = mapa_times.get(time_id_externo)
        if time_id is None or player_id is None:
            return None
        nome, posicao = info_jogadores.get(player_id, (nome_fallback, None))
        jogador = upsert_jogador(db, cache_jogadores, player_id, nome or nome_fallback, posicao, time_id)
        if player_id not in estatisticas:
            estatisticas[player_id] = {
                "jogador": jogador,
                "time_id": time_id,
                "gols": 0,
                "assistencias": 0,
                "cartoes_amarelos": 0,
                "cartoes_vermelhos": 0,
            }
        return estatisticas[player_id]

    # titulares -- garantidamente jogaram, contam mesmo sem nenhum evento
    for time_id_externo, bloco in mapa_bloco.items():
        for linha in bloco.get("initialLineup", []):
            for j in linha:
                registrar(j["id"], j["name"], time_id_externo)

    for evento in events:
        time_id_externo = evento.get("team", {}).get("id")
        tipo = evento.get("type")
        player_id = evento.get("playerId")
        player_nome = evento.get("player")

        if tipo == "Substitution":
            registrar(player_id, player_nome, time_id_externo)  # quem ENTROU
            continue

        stats = registrar(player_id, player_nome, time_id_externo)
        if stats is None:
            continue

        if tipo in ("Goal", "Penalty"):
            # Highlightly marca gol de penalti com type="Penalty", nao
            # "Goal" -- sem esse `in`, todo penalti convertido ficava de
            # fora da contagem de gols do jogador (bug real, encontrado
            # 2026-08-25 investigando 58 partidas onde a soma dos gols
            # por jogador nao batia com o placar real).
            stats["gols"] += 1
            assist_id = evento.get("assistingPlayerId")
            if assist_id:
                assist_stats = registrar(assist_id, evento.get("assist"), time_id_externo)
                if assist_stats:
                    assist_stats["assistencias"] += 1
        elif tipo == "Yellow Card":
            stats["cartoes_amarelos"] += 1
        elif tipo in ("Red Card", "Second Yellow Card"):
            stats["cartoes_vermelhos"] += 1
        # type == "Own Goal": o jogador e' registrado (aparicao conta),
        # mas o gol NAO e' somado ao "gols" dele -- convencao padrao de
        # estatistica de futebol (gol contra nao e' credito pessoal do
        # jogador). Por isso a soma dos gols por jogador de uma partida
        # com gol contra fica, de proposito, 1 a menos que o placar real.

    novas = 0
    for dados in estatisticas.values():
        ja_existe = (
            db.query(EstatisticaJogadorPartida)
            .filter(
                EstatisticaJogadorPartida.jogador_id == dados["jogador"].id,
                EstatisticaJogadorPartida.partida_id == partida.id,
            )
            .first()
        )
        if ja_existe:
            continue
        db.add(
            EstatisticaJogadorPartida(
                jogador_id=dados["jogador"].id,
                partida_id=partida.id,
                time_id=dados["time_id"],
                gols=dados["gols"],
                assistencias=dados["assistencias"],
                cartoes_amarelos=dados["cartoes_amarelos"],
                cartoes_vermelhos=dados["cartoes_vermelhos"],
            )
        )
        novas += 1

    db.commit()
    return novas, None


def importar_jogadores(limite=MAX_PARTIDAS_POR_EXECUCAO):
    if not API_KEY:
        print("ERRO: HIGHLIGHTLY_API_KEY não encontrada no .env")
        return

    db = SessionLocal()
    cache_jogadores = {}

    try:
        partidas = (
            db.query(Partida)
            .filter(Partida.status == "finalizada", Partida.id_externo.isnot(None))
            .order_by(Partida.data.desc())
            .all()
        )

        ja_processadas_ids = {
            row[0] for row in db.query(EstatisticaJogadorPartida.partida_id).distinct().all()
        }
        pendentes = [p for p in partidas if p.id not in ja_processadas_ids]

        print(
            f"{len(pendentes)} partidas ainda sem estatistica de jogador "
            f"(de {len(partidas)} finalizadas com id_externo)."
        )

        processadas = 0
        for partida in pendentes:
            if processadas >= limite:
                print(f"\nLimite de {limite} partidas por execução atingido. Rode de novo depois.")
                break

            try:
                novas, erro = processar_partida(db, partida, cache_jogadores)
            except CotaExcedidaError:
                db.rollback()
                print(
                    "\nCota da API excedida. Progresso salvo (cada partida ja foi commitada "
                    "individualmente ate aqui). Rode de novo amanha."
                )
                break
            except Exception as e:
                db.rollback()
                print(f"  Pulando partida {partida.id} (id_externo={partida.id_externo}): erro inesperado -- {e}")
                continue

            if erro:
                print(f"  Pulando partida {partida.id} (id_externo={partida.id_externo}): {erro}")
                continue

            print(
                f"  rodada {partida.rodada}: {partida.time_mandante.nome} x {partida.time_visitante.nome} "
                f"-- {novas} jogadores com estatistica nova"
            )
            processadas += 1

        print(f"\nImportação de jogadores concluída. {processadas} partidas processadas nessa execução.")
    finally:
        db.close()


if __name__ == "__main__":
    importar_jogadores()
