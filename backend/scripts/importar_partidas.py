import os
import re
from datetime import date, timedelta
import requests
from dotenv import load_dotenv

from app.database import SessionLocal
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

DIAS_PARA_TRAS = 30           # até quantos dias no passado vamos escanear
MAX_IMPORTACOES_POR_EXECUCAO = 40  # limite de segurança para não estourar a cota diária (100 req/dia)


def buscar_partidas_por_data(dia_str):
    resp = requests.get(
        f"{BASE_URL}/matches",
        headers=HEADERS,
        params={"leagueId": LEAGUE_ID_BRASILEIRAO, "date": dia_str, "limit": 20},
    )
    resp.raise_for_status()
    return resp.json().get("data", [])


def buscar_estatisticas(match_id):
    resp = requests.get(f"{BASE_URL}/statistics/{match_id}", headers=HEADERS)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()


def buscar_detalhe_partida(match_id):
    resp = requests.get(f"{BASE_URL}/matches/{match_id}", headers=HEADERS)
    resp.raise_for_status()
    dados = resp.json()
    # o endpoint devolve uma lista com um único item, não o objeto direto
    if isinstance(dados, list):
        return dados[0] if dados else None
    return dados


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


def importar():
    if not API_KEY:
        print("ERRO: HIGHLIGHTLY_API_KEY não encontrada no .env")
        return

    db = SessionLocal()
    importadas = 0
    ja_existiam = 0
    ignoradas_sem_time = 0

    try:
        hoje = date.today()

        for i in range(1, DIAS_PARA_TRAS + 1):
            if importadas >= MAX_IMPORTACOES_POR_EXECUCAO:
                print(f"\nLimite de {MAX_IMPORTACOES_POR_EXECUCAO} importações por execução atingido. Pare e rode de novo depois.")
                break

            dia = hoje - timedelta(days=i)
            dia_str = dia.strftime("%Y-%m-%d")

            partidas_do_dia = buscar_partidas_por_data(dia_str)
            if not partidas_do_dia:
                continue

            for p in partidas_do_dia:
                if importadas >= MAX_IMPORTACOES_POR_EXECUCAO:
                    break

                estado = p.get("state", {}).get("description", "")
                if "Finished" not in estado and "Full-time" not in estado and "FT" not in estado:
                    continue

                id_externo = p["id"]

                ja_no_banco = db.query(Partida).filter(Partida.id_externo == id_externo).first()
                if ja_no_banco:
                    ja_existiam += 1
                    continue

                time_mandante = db.query(Time).filter(Time.id_externo == p["homeTeam"]["id"]).first()
                time_visitante = db.query(Time).filter(Time.id_externo == p["awayTeam"]["id"]).first()

                if not time_mandante or not time_visitante:
                    print(f"  Pulando partida {id_externo}: time não cadastrado no banco "
                          f"({p['homeTeam']['name']} x {p['awayTeam']['name']}) — rode sincronizar_times.py")
                    ignoradas_sem_time += 1
                    continue

                detalhe = buscar_detalhe_partida(id_externo)
                if not detalhe:
                    print(f"  Pulando partida {id_externo}: detalhe não encontrado")
                    continue

                gols_mandante, gols_visitante = parse_placar(detalhe["state"]["score"]["current"])
                rodada = parse_rodada(detalhe.get("round"))

                stats = buscar_estatisticas(id_externo)
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

                nova_partida = Partida(
                    id_externo=id_externo,
                    time_mandante_id=time_mandante.id,
                    time_visitante_id=time_visitante.id,
                    gols_mandante=gols_mandante,
                    gols_visitante=gols_visitante,
                    data=dia,
                    rodada=rodada,
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
                db.add(nova_partida)
                db.commit()

                print(f"  Importada: {p['homeTeam']['name']} {gols_mandante} x {gols_visitante} "
                      f"{p['awayTeam']['name']} ({dia_str})")
                importadas += 1

        print(f"\nImportação concluída. {importadas} partidas novas importadas, "
              f"{ja_existiam} já existiam, {ignoradas_sem_time} ignoradas por time não cadastrado.")

    finally:
        db.close()


if __name__ == "__main__":
    importar()