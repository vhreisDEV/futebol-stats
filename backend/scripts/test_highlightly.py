import os
import json
from datetime import date, timedelta
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("HIGHLIGHTLY_API_KEY")
BASE_URL = "https://soccer.highlightly.net"

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "soccer.highlightly.net",
}


def buscar_ligas_brasil():
    resp = requests.get(
        f"{BASE_URL}/leagues",
        headers=HEADERS,
        params={"countryName": "Brazil"},
    )
    resp.raise_for_status()
    return resp.json().get("data", [])


def buscar_partidas_por_data(league_id, data_str):
    resp = requests.get(
        f"{BASE_URL}/matches",
        headers=HEADERS,
        params={"leagueId": league_id, "date": data_str, "limit": 20},
    )
    resp.raise_for_status()
    return resp.json().get("data", [])


def buscar_estatisticas(match_id):
    resp = requests.get(f"{BASE_URL}/statistics/{match_id}", headers=HEADERS)
    if resp.status_code == 404:
        print("  Sem estatísticas disponíveis para essa partida.")
        return None
    resp.raise_for_status()
    return resp.json()


def buscar_detalhe_partida(match_id):
    resp = requests.get(f"{BASE_URL}/matches/{match_id}", headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


def buscar_standings(league_id, season):
    resp = requests.get(
        f"{BASE_URL}/standings",
        headers=HEADERS,
        params={"leagueId": league_id, "season": season},
    )
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    if not API_KEY:
        print("ERRO: HIGHLIGHTLY_API_KEY não encontrada no .env")
        exit(1)

    ligas = buscar_ligas_brasil()
    brasileirao = next(
        (l for l in ligas if "Serie A" in l["name"] or "Série A" in l["name"]),
        None,
    )

    if not brasileirao:
        print("Brasileirão Série A não encontrado.")
        exit(0)

    print(f"Brasileirão Série A: id={brasileirao['id']}\n")

    hoje = date.today()
    partida_escolhida = None

    for i in range(1, 30):
        dia = hoje - timedelta(days=i)
        dia_str = dia.strftime("%Y-%m-%d")
        partidas = buscar_partidas_por_data(brasileirao["id"], dia_str)

        if not partidas:
            continue

        print(f"{dia_str}: {len(partidas)} partida(s) encontrada(s)")

        for p in partidas:
            estado = p.get("state", {}).get("description", "")
            print(f"  #{p['id']} | {p['homeTeam']['name']} x {p['awayTeam']['name']} | estado: {estado}")
            if "Finished" in estado or "Full-time" in estado or "FT" in estado:
                partida_escolhida = p
                break

        if partida_escolhida:
            break

    if not partida_escolhida:
        print("\nNão encontrei nenhuma partida finalizada nos últimos 30 dias.")
        exit(0)

    print(f"\nPartida finalizada encontrada: #{partida_escolhida['id']} "
          f"({partida_escolhida['homeTeam']['name']} x {partida_escolhida['awayTeam']['name']})")

    stats = buscar_estatisticas(partida_escolhida["id"])
    if stats:
        print("\nEstatísticas retornadas:")
        for time_stats in stats:
            print(f"\n  Time: {time_stats['team']['name']}")
            for stat in time_stats.get("statistics", []):
                print(f"    {stat['displayName']}: {stat['value']}")

    detalhe = buscar_detalhe_partida(partida_escolhida["id"])
    print("\nDetalhe bruto da partida:")
    print(json.dumps(detalhe, indent=2, ensure_ascii=False))

    standings = buscar_standings(brasileirao["id"], 2026)
    print("\nStandings (classificação e times):")
    print(json.dumps(standings, indent=2, ensure_ascii=False))