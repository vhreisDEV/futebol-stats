# -*- coding: utf-8 -*-
"""
Sincroniza so' status/placar/data de TODAS as ligas com times ja
cadastrados, sem gastar cota nenhuma em estatisticas -- pensado pra
rodar sempre PRIMEIRO no dia, antes de qualquer outro script gastar
cota. Listar a temporada inteira via /matches e' barato e paginado (1
chamada a cada 100 partidas) e cobre uma liga inteira de uma vez: ~2
chamadas pra La Liga, ~2 pra Premier League, ~4 pro Brasileirao -- por
volta de 8 chamadas no total pra sincronizar status de tudo.

Bug real que motivou esse script, 2026-08-26: encontramos 3 partidas
da La Liga com data ja passada mas ainda marcadas "agendada" -- nao
era falta de dado na Highlightly, era so' que importar_partidas.py
roda uma liga de cada vez e a cota tende a se esgotar (no Brasileirao,
ou em investigacoes avulsas) antes de chegar nas outras ligas. Essa
sincronizacao de status nao depende de sobrar cota pra estatisticas,
entao pode/deve rodar todo dia sem risco de ficar pela metade.

Partida que vira "finalizada" aqui fica com o placar certo mas SEM
estatisticas (escanteios/chutes/cartoes ficam None) -- importar_partidas.py
ja sabe enriquecer esse caso depois (tem_estatisticas_completas() ==
False), entao rodar os dois scripts nao duplica trabalho nenhum, so'
completa o que falta quando tiver cota sobrando.

Uso (de dentro de backend/; local usa SQLite, ver
sincronizar_status_partidas_producao.py pra producao):
    py scripts/sincronizar_status_partidas.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.campeonato import Campeonato
from app.models.time import Time
from app.models.partida import Partida
from scripts.importar_partidas import (
    API_KEY,
    buscar_partida_existente,
    buscar_temporada_completa,
    mapear_status,
    parse_data_hora,
    parse_placar,
    parse_rodada,
    tem_estatisticas_completas,
)


def sincronizar_liga(db, campeonato):
    partidas_temporada = buscar_temporada_completa(campeonato.id_externo_liga, campeonato.temporada)
    criadas = 0
    atualizadas = 0
    sem_mudanca = 0

    for p in partidas_temporada:
        id_externo = p["id"]

        time_mandante = db.query(Time).filter(Time.id_externo == p["homeTeam"]["id"]).first()
        time_visitante = db.query(Time).filter(Time.id_externo == p["awayTeam"]["id"]).first()
        if not time_mandante or not time_visitante:
            continue

        estado = p.get("state", {}).get("description", "")
        status_novo = mapear_status(estado)
        rodada = parse_rodada(p.get("round"))
        data_partida, hora_partida = parse_data_hora(p["date"])

        gols_mandante = gols_visitante = None
        if status_novo == "finalizada":
            score_atual = p.get("state", {}).get("score", {}).get("current")
            if not score_atual:
                continue
            gols_mandante, gols_visitante = parse_placar(score_atual)

        partida = buscar_partida_existente(db, id_externo, rodada, time_mandante.id, time_visitante.id)

        if partida and partida.status == "finalizada" and tem_estatisticas_completas(partida):
            # Ja tem placar E estatisticas completas -- so' confere que nao
            # ha divergencia de placar (nunca sobrescreve dado ja enriquecido
            # so' com base nessa listagem barata, mesma cautela do
            # importar_partidas.py pra esse caso).
            if status_novo == "finalizada" and (partida.gols_mandante, partida.gols_visitante) != (
                gols_mandante,
                gols_visitante,
            ):
                print(
                    f"  AVISO: partida id={partida.id} (id_externo={id_externo}) tem placar divergente "
                    f"({partida.gols_mandante}x{partida.gols_visitante} salvo vs {gols_mandante}x{gols_visitante} "
                    f"da API) -- nao sobrescrito, checar manualmente."
                )
            sem_mudanca += 1
            continue

        if partida:
            mudou = (
                partida.status != status_novo
                or partida.data != data_partida
                or partida.id_externo != id_externo
                or partida.rodada != rodada
                or (status_novo == "finalizada" and (partida.gols_mandante, partida.gols_visitante) != (
                    gols_mandante,
                    gols_visitante,
                ))
            )
            if not mudou:
                sem_mudanca += 1
                continue

            partida.id_externo = id_externo
            partida.status = status_novo
            partida.data = data_partida
            if partida.hora is None:
                partida.hora = hora_partida
            partida.rodada = rodada
            if status_novo == "finalizada":
                partida.gols_mandante = gols_mandante
                partida.gols_visitante = gols_visitante
            atualizadas += 1
        else:
            db.add(
                Partida(
                    id_externo=id_externo,
                    campeonato_id=campeonato.id,
                    time_mandante_id=time_mandante.id,
                    time_visitante_id=time_visitante.id,
                    status=status_novo,
                    gols_mandante=gols_mandante,
                    gols_visitante=gols_visitante,
                    data=data_partida,
                    hora=hora_partida,
                    rodada=rodada,
                )
            )
            criadas += 1
        db.commit()

    return criadas, atualizadas, sem_mudanca


def sincronizar_todas():
    if not API_KEY:
        print("ERRO: HIGHLIGHTLY_API_KEY não encontrada no .env")
        return

    db = SessionLocal()
    try:
        campeonatos = db.query(Campeonato).filter(Campeonato.id_externo_liga.isnot(None)).all()
        for campeonato in campeonatos:
            tem_times = db.query(Time).filter(Time.campeonato_id == campeonato.id).first() is not None
            if not tem_times:
                print(f"{campeonato.nome}: sem times cadastrados ainda, pulando (rode sincronizar_times.py primeiro).")
                continue

            criadas, atualizadas, sem_mudanca = sincronizar_liga(db, campeonato)
            print(
                f"{campeonato.nome}: {criadas} criada(s), {atualizadas} atualizada(s), "
                f"{sem_mudanca} já corretas."
            )
    finally:
        db.close()


if __name__ == "__main__":
    sincronizar_todas()
