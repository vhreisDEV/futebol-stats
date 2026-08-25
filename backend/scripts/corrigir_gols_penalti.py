# -*- coding: utf-8 -*-
"""
Corrige partidas ja importadas onde a soma dos gols creditados por
jogador (EstatisticaJogadorPartida.gols) ficou menor que o placar real
(Partida.gols_mandante + gols_visitante). Investigado 2026-08-25:
Highlightly marca gol de penalti com type="Penalty" (nao "Goal"), e
importar_jogadores.py so somava "Goal" -- todo penalti convertido ficava
de fora da contagem de gols do jogador. Ja corrigido pra importacoes
futuras (ver processar_partida em importar_jogadores.py); este script
so re-processa o que ja foi importado errado.

NAO mexe em gol contra ("Own Goal") -- por convencao de estatistica de
futebol, gol contra nao conta como gol do proprio jogador, entao uma
partida com gol contra continua, de proposito, com a soma 1 a menos que
o placar real depois desta correcao.

So usa 1 chamada de API por partida afetada (so /events -- os jogadores
ja existem no banco desde a importacao original, nao precisa de
/lineups de novo).

Uso (de dentro de backend/; local usa SQLite, ver
corrigir_gols_penalti_producao.py pra produção):
    py scripts/corrigir_gols_penalti.py          # aplica de verdade
    py scripts/corrigir_gols_penalti.py --dry-run  # so mostra o que mudaria
"""
import os
import sys

import requests
from dotenv import load_dotenv
from sqlalchemy import func

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.time import Time  # noqa: F401 -- precisa estar importado pro relationship de Partida/Estatistica resolver
from app.models.partida import Partida
from app.models.jogador import Jogador
from app.models.estatistica_jogador_partida import EstatisticaJogadorPartida

load_dotenv()

API_KEY = os.getenv("HIGHLIGHTLY_API_KEY")
BASE_URL = "https://soccer.highlightly.net"
HEADERS = {"x-rapidapi-key": API_KEY}


class CotaExcedidaError(Exception):
    pass


def buscar_events(match_id):
    resp = requests.get(f"{BASE_URL}/events/{match_id}", headers=HEADERS)
    if resp.status_code == 429:
        raise CotaExcedidaError()
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()


def encontrar_partidas_divergentes(db, campeonato_id=None):
    query = db.query(Partida).filter(Partida.status == "finalizada", Partida.id_externo.isnot(None))
    if campeonato_id is not None:
        query = query.filter(Partida.campeonato_id == campeonato_id)
    partidas = query.all()
    gols_por_partida = dict(
        db.query(EstatisticaJogadorPartida.partida_id, func.coalesce(func.sum(EstatisticaJogadorPartida.gols), 0))
        .group_by(EstatisticaJogadorPartida.partida_id)
        .all()
    )

    divergentes = []
    for p in partidas:
        real = (p.gols_mandante or 0) + (p.gols_visitante or 0)
        creditado = gols_por_partida.get(p.id, 0)
        if real != creditado:
            divergentes.append(p)
    return divergentes


def corrigir_partida(db, partida, dry_run):
    events = buscar_events(partida.id_externo)
    if events is None:
        return "sem events disponiveis"

    # Recalcula do ZERO o total correto de gols (Goal + Penalty) de cada
    # jogador que aparece em algum desses eventos, em vez de incrementar
    # `+1` em cima do valor atual -- isso mantem a correcao idempotente
    # (rodar o script de novo pra uma partida ja corrigida, por exemplo
    # porque ela continua "divergente" so por causa de um gol contra que
    # nunca sera contado, da o mesmo resultado em vez de somar o penalti
    # duas vezes).
    total_correto_por_jogador = {}
    penaltis_por_jogador = {}
    for evento in events:
        tipo = evento.get("type")
        if tipo not in ("Goal", "Penalty"):
            continue
        player_id_externo = evento.get("playerId")
        total_correto_por_jogador[player_id_externo] = total_correto_por_jogador.get(player_id_externo, 0) + 1
        if tipo == "Penalty":
            penaltis_por_jogador[player_id_externo] = evento.get("time")

    aplicadas = []
    for player_id_externo, total_correto in total_correto_por_jogador.items():
        if player_id_externo not in penaltis_por_jogador:
            continue  # sem penalti pra esse jogador nessa partida -- import original ja contou certo

        jogador = db.query(Jogador).filter(Jogador.id_externo == player_id_externo).first()
        if not jogador:
            nome = next((e.get("player") for e in events if e.get("playerId") == player_id_externo), "?")
            aplicadas.append(f"AVISO: jogador id_externo={player_id_externo} ({nome}) nao encontrado no banco")
            continue

        linha = (
            db.query(EstatisticaJogadorPartida)
            .filter(
                EstatisticaJogadorPartida.jogador_id == jogador.id,
                EstatisticaJogadorPartida.partida_id == partida.id,
            )
            .first()
        )
        if not linha:
            aplicadas.append(f"AVISO: sem linha de estatistica pra {jogador.nome} nessa partida, pulando")
            continue

        if linha.gols == total_correto:
            continue  # ja esta certo (correcao anterior ja aplicada)

        aplicadas.append(
            f"{jogador.nome}: gols {linha.gols} -> {total_correto} "
            f"(penalti min {penaltis_por_jogador[player_id_externo]})"
        )
        if not dry_run:
            linha.gols = total_correto

    if not dry_run:
        db.commit()
    return aplicadas


def corrigir(dry_run=True, campeonato_id=None):
    if not API_KEY:
        print("ERRO: HIGHLIGHTLY_API_KEY não encontrada no .env")
        return

    db = SessionLocal()
    try:
        divergentes = encontrar_partidas_divergentes(db, campeonato_id)
        escopo = f"campeonato_id={campeonato_id}" if campeonato_id is not None else "todos os campeonatos"
        print(f"{len(divergentes)} partidas com divergencia de gols ({escopo}).")
        print(f"Modo: {'DRY RUN (nada sera salvo)' if dry_run else 'APLICANDO DE VERDADE'}\n")

        for partida in divergentes:
            try:
                resultado = corrigir_partida(db, partida, dry_run)
            except CotaExcedidaError:
                print("Cota da Highlightly excedida (429). Pare e rode de novo mais tarde.")
                break

            if isinstance(resultado, str):
                print(f"Partida {partida.id} (ext {partida.id_externo}): {resultado}")
            elif resultado:
                print(f"Partida {partida.id} (ext {partida.id_externo}):")
                for linha in resultado:
                    print(f"  - {linha}")
            else:
                print(f"Partida {partida.id} (ext {partida.id_externo}): nenhum evento 'Penalty' encontrado (divergencia deve ser gol contra)")
    finally:
        db.close()


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    corrigir(dry_run=dry_run)
