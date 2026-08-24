import os
import re
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

from app.database import SessionLocal
from app.models.campeonato import Campeonato
from app.models.time import Time
from app.models.partida import Partida

load_dotenv()

API_KEY = os.getenv("HIGHLIGHTLY_API_KEY")
BASE_URL = "https://soccer.highlightly.net"

HEADERS = {
    "x-rapidapi-key": API_KEY,
}

LEAGUE_ID_BRASILEIRAO = 61205
SEASON = 2026

MAX_IMPORTACOES_POR_EXECUCAO = 90  # limite de seguranca para nao estourar a cota diaria (100 req/dia)


def buscar_temporada_completa():
    # Lista a temporada inteira paginada (id, rodada, placar, times, status
    # de cada partida ja vem nessa resposta -- nao precisa de uma chamada
    # extra por partida so pra pegar isso).
    partidas = []
    offset = 0
    limit = 100

    while True:
        resp = requests.get(
            f"{BASE_URL}/matches",
            headers=HEADERS,
            params={"leagueId": LEAGUE_ID_BRASILEIRAO, "season": SEASON, "limit": limit, "offset": offset},
        )
        if resp.status_code == 429:
            print(f"  Cota excedida ao listar a temporada (offset {offset}). "
                  f"Usando as {len(partidas)} partidas já listadas nessa execução.")
            break
        resp.raise_for_status()
        dados = resp.json()
        partidas.extend(dados.get("data", []))

        total = dados.get("pagination", {}).get("totalCount", len(partidas))
        offset += limit
        if offset >= total:
            break

    return partidas


class CotaExcedidaError(Exception):
    pass


def buscar_estatisticas(match_id):
    resp = requests.get(f"{BASE_URL}/statistics/{match_id}", headers=HEADERS)
    if resp.status_code == 404:
        return None
    if resp.status_code == 429:
        raise CotaExcedidaError()
    resp.raise_for_status()
    return resp.json()


def parse_placar(score_str):
    # formato esperado: "2 - 0" (mandante - visitante)
    partes = score_str.split(" - ")
    return int(partes[0]), int(partes[1])


def parse_rodada(round_str):
    # formato esperado: "Regular Season - 22"
    if not round_str:
        return None
    match = re.search(r"(\d+)\s*$", round_str)
    return int(match.group(1)) if match else None


FUSO_BRT = timedelta(hours=-3)  # Brasil nao usa horario de verao desde 2019 -- BRT = UTC-3 sempre


def parse_data_hora(data_iso):
    # formato esperado: "2026-07-16T22:30:00.000Z" (sempre em UTC). Converte
    # pra BRT antes de separar data/hora -- jogos que rolam tarde da noite
    # (20:30-21:30 BRT) viram madrugada em UTC e cairiam no dia seguinte se
    # a gente so truncasse o UTC direto (bug historico, antes remendado a
    # mao partida por partida -- essa conversao resolve na raiz).
    dt_utc = datetime.fromisoformat(data_iso.replace("Z", "+00:00"))
    dt_brt = dt_utc + FUSO_BRT
    return dt_brt.date(), dt_brt.time()


def mapear_status(estado):
    # Confirmado com dado real (rodada 21, 2026-08-18): a Highlightly usa
    # exatamente "Postponed" em state.description para partida adiada.
    if "Finished" in estado or "Full-time" in estado or "FT" in estado:
        return "finalizada"
    if "Postponed" in estado or "Adiad" in estado or "Suspended" in estado:
        return "adiada"
    return "agendada"


def extrair_stat(lista_stats, nome_procurado):
    for stat in lista_stats:
        if stat["displayName"] == nome_procurado:
            return stat["value"]
    return 0


def mapear_estatisticas_time(lista_stats):
    chutes_on = extrair_stat(lista_stats, "Shots on target")
    chutes_off = extrair_stat(lista_stats, "Shots off target")
    chutes_blocked = extrair_stat(lista_stats, "Blocked shots")

    return {
        "escanteios": int(extrair_stat(lista_stats, "Corners")),
        "chutes": int(chutes_on + chutes_off + chutes_blocked),
        "chutes_gol": int(chutes_on),
        "cartoes_amarelos": int(extrair_stat(lista_stats, "Yellow cards")),
        "cartoes_vermelhos": int(extrair_stat(lista_stats, "Red cards")),
    }


def tem_estatisticas_completas(partida):
    # Uma partida "finalizada" pode ter vindo so do PDF (goals only, via
    # preencher_placares_pdf.py) -- so tem gol de verdade quando tambem tem
    # escanteios, o resto das estatisticas vem junto na mesma chamada da API.
    return partida.escanteios_mandante is not None


def buscar_partida_existente(db, id_externo, rodada, time_mandante_id, time_visitante_id):
    # Primeiro tenta pelo id externo (partida ja importada de verdade antes).
    partida = db.query(Partida).filter(Partida.id_externo == id_externo).first()
    if partida:
        return partida

    # Senao, pode ser um placeholder agendada/adiada pre-cadastrado (via
    # backfill_calendario_2026.py ou uma execucao anterior deste script)
    # que ainda nao tem id_externo -- reaproveita a linha em vez de duplicar
    # o confronto.
    return (
        db.query(Partida)
        .filter(
            Partida.id_externo.is_(None),
            Partida.rodada == rodada,
            Partida.time_mandante_id == time_mandante_id,
            Partida.time_visitante_id == time_visitante_id,
        )
        .first()
    )


def importar():
    if not API_KEY:
        print("ERRO: HIGHLIGHTLY_API_KEY não encontrada no .env")
        return

    db = SessionLocal()
    campeonato = db.query(Campeonato).filter(Campeonato.id_externo_liga == LEAGUE_ID_BRASILEIRAO).first()
    if not campeonato:
        print("ERRO: Campeonato do Brasileirao nao encontrado (rode a migracao/seed do Campeonato primeiro).")
        return

    importadas = 0
    enriquecidas = 0
    placeholders = 0
    ja_existiam = 0
    ignoradas_sem_time = 0

    try:
        partidas_temporada = buscar_temporada_completa()
        print(f"{len(partidas_temporada)} partidas na temporada (todas as rodadas).\n")

        for p in partidas_temporada:
            if importadas + enriquecidas >= MAX_IMPORTACOES_POR_EXECUCAO:
                print(f"\nLimite de {MAX_IMPORTACOES_POR_EXECUCAO} importações por execução atingido. Rode de novo depois.")
                break

            id_externo = p["id"]

            time_mandante = db.query(Time).filter(Time.id_externo == p["homeTeam"]["id"]).first()
            time_visitante = db.query(Time).filter(Time.id_externo == p["awayTeam"]["id"]).first()

            if not time_mandante or not time_visitante:
                print(f"  Pulando partida {id_externo}: time não cadastrado no banco "
                      f"({p['homeTeam']['name']} x {p['awayTeam']['name']}) — rode sincronizar_times.py")
                ignoradas_sem_time += 1
                continue

            estado = p.get("state", {}).get("description", "")
            status = mapear_status(estado)
            rodada = parse_rodada(p.get("round"))
            data_partida, hora_partida = parse_data_hora(p["date"])

            partida_existente = buscar_partida_existente(
                db, id_externo, rodada, time_mandante.id, time_visitante.id
            )

            if (
                partida_existente
                and partida_existente.status == "finalizada"
                and tem_estatisticas_completas(partida_existente)
            ):
                # Ja importamos essa partida com placar e estatisticas antes.
                ja_existiam += 1
                continue

            if status != "finalizada":
                # Agendada ou adiada: so precisa dos dados basicos, sem gastar
                # chamada nenhuma de estatisticas -- nao ha placar/stats pra
                # buscar ainda.
                if partida_existente:
                    partida_existente.id_externo = id_externo
                    partida_existente.status = status
                    partida_existente.data = data_partida
                    partida_existente.hora = hora_partida
                else:
                    db.add(Partida(
                        id_externo=id_externo,
                        campeonato_id=campeonato.id,
                        time_mandante_id=time_mandante.id,
                        time_visitante_id=time_visitante.id,
                        status=status,
                        data=data_partida,
                        hora=hora_partida,
                        rodada=rodada,
                    ))
                db.commit()
                print(f"  {status.upper()}: rodada {rodada} — {p['homeTeam']['name']} x "
                      f"{p['awayTeam']['name']} ({data_partida})")
                placeholders += 1
                continue

            score_atual = p.get("state", {}).get("score", {}).get("current")
            if not score_atual:
                print(f"  Pulando partida {id_externo}: marcada como finalizada mas sem placar disponível")
                continue

            gols_mandante, gols_visitante = parse_placar(score_atual)

            enriquecendo = bool(
                partida_existente
                and partida_existente.status == "finalizada"
                and not tem_estatisticas_completas(partida_existente)
            )
            if enriquecendo and (partida_existente.gols_mandante, partida_existente.gols_visitante) != (
                gols_mandante,
                gols_visitante,
            ):
                print(
                    f"  Pulando partida {id_externo}: placar da API ({gols_mandante} x {gols_visitante}) "
                    f"diverge do ja salvo ({partida_existente.gols_mandante} x {partida_existente.gols_visitante}) "
                    f"-- checar manualmente, rodada {rodada}"
                )
                continue

            try:
                stats = buscar_estatisticas(id_externo)
            except CotaExcedidaError:
                print(f"\nCota da API excedida. Progresso salvo (cada partida ja foi commitada "
                      f"individualmente ate aqui). Rode de novo amanha pra continuar.")
                break
            if not stats:
                print(f"  Pulando partida {id_externo}: sem estatísticas disponíveis")
                continue

            stats_mandante = next((s for s in stats if s["team"]["id"] == p["homeTeam"]["id"]), None)
            stats_visitante = next((s for s in stats if s["team"]["id"] == p["awayTeam"]["id"]), None)

            if not stats_mandante or not stats_visitante:
                print(f"  Pulando partida {id_externo}: estatísticas incompletas")
                continue

            m = mapear_estatisticas_time(stats_mandante["statistics"])
            v = mapear_estatisticas_time(stats_visitante["statistics"])

            dados_estatisticas = dict(
                escanteios_mandante=m["escanteios"],
                escanteios_visitante=v["escanteios"],
                escanteios_1t_mandante=None,
                escanteios_1t_visitante=None,
                escanteios_2t_mandante=None,
                escanteios_2t_visitante=None,
                chutes_mandante=m["chutes"],
                chutes_visitante=v["chutes"],
                chutes_1t_mandante=None,
                chutes_1t_visitante=None,
                chutes_gol_mandante=m["chutes_gol"],
                chutes_gol_visitante=v["chutes_gol"],
                cartoes_amarelos_mandante=m["cartoes_amarelos"],
                cartoes_amarelos_visitante=v["cartoes_amarelos"],
                cartoes_vermelhos_mandante=m["cartoes_vermelhos"],
                cartoes_vermelhos_visitante=v["cartoes_vermelhos"],
            )

            if enriquecendo:
                # So completa as estatisticas que faltavam -- gols, data,
                # rodada e status ja estao corretos (inclusive datas
                # corrigidas manualmente pro fuso BRT), nao mexe neles. Hora
                # e excecao: partidas antigas nunca tiveram esse campo, entao
                # preencher se ainda estiver vazio e' seguro (nao sobrescreve
                # nada que ja existia).
                partida_existente.id_externo = id_externo
                if partida_existente.hora is None:
                    partida_existente.hora = hora_partida
                for campo, valor in dados_estatisticas.items():
                    setattr(partida_existente, campo, valor)
            else:
                dados_finalizada = dict(
                    id_externo=id_externo,
                    campeonato_id=campeonato.id,
                    time_mandante_id=time_mandante.id,
                    time_visitante_id=time_visitante.id,
                    status="finalizada",
                    gols_mandante=gols_mandante,
                    gols_visitante=gols_visitante,
                    data=data_partida,
                    hora=hora_partida,
                    rodada=rodada,
                    **dados_estatisticas,
                )
                if partida_existente:
                    for campo, valor in dados_finalizada.items():
                        setattr(partida_existente, campo, valor)
                else:
                    db.add(Partida(**dados_finalizada))
            db.commit()

            if enriquecendo:
                print(f"  Enriquecida: rodada {rodada} — {p['homeTeam']['name']} {gols_mandante} x {gols_visitante} "
                      f"{p['awayTeam']['name']} (estatisticas completas adicionadas)")
                enriquecidas += 1
            else:
                print(f"  Importada: rodada {rodada} — {p['homeTeam']['name']} {gols_mandante} x {gols_visitante} "
                      f"{p['awayTeam']['name']} ({data_partida})")
                importadas += 1

        print(f"\nImportação concluída. {importadas} partidas finalizadas importadas, "
              f"{enriquecidas} enriquecidas com estatisticas completas, "
              f"{placeholders} agendadas/adiadas registradas, {ja_existiam} já existiam completas, "
              f"{ignoradas_sem_time} ignoradas por time não cadastrado.")

    finally:
        db.close()


if __name__ == "__main__":
    importar()
