import os
import requests
from dotenv import load_dotenv

from app.database import SessionLocal
from app.models.campeonato import Campeonato
from app.models.time import Time

load_dotenv()

API_KEY = os.getenv("HIGHLIGHTLY_API_KEY")
BASE_URL = "https://soccer.highlightly.net"

HEADERS = {
    "x-rapidapi-key": API_KEY,
}

LEAGUE_ID_BRASILEIRAO = 61205
SEASON = 2026


def buscar_ligas_brasil():
    resp = requests.get(
        f"{BASE_URL}/leagues",
        headers=HEADERS,
        params={"countryName": "Brazil"},
    )
    resp.raise_for_status()
    return resp.json().get("data", [])


def buscar_standings(league_id, season):
    resp = requests.get(
        f"{BASE_URL}/standings",
        headers=HEADERS,
        params={"leagueId": league_id, "season": season},
    )
    resp.raise_for_status()
    return resp.json()


def extrair_times_do_standings(standings):
    times = []
    for grupo in standings.get("groups", []):
        for item in grupo.get("standings", []):
            time_info = item.get("team", {})
            if time_info.get("id") and time_info.get("name"):
                times.append(time_info)
    return times


def sincronizar():
    if not API_KEY:
        print("ERRO: HIGHLIGHTLY_API_KEY não encontrada no .env")
        return

    db = SessionLocal()

    try:
        campeonato = db.query(Campeonato).filter(Campeonato.id_externo_liga == LEAGUE_ID_BRASILEIRAO).first()
        if not campeonato:
            print("ERRO: Campeonato do Brasileirao nao encontrado (rode a migracao/seed do Campeonato primeiro).")
            return

        standings = buscar_standings(LEAGUE_ID_BRASILEIRAO, SEASON)
        times_api = extrair_times_do_standings(standings)

        print(f"{len(times_api)} times encontrados na Highlightly para o Brasileirão {SEASON}.\n")

        criados = 0
        ja_existiam = 0

        for time_api in times_api:
            id_externo = time_api["id"]
            nome = time_api["name"]

            time_existente = db.query(Time).filter(Time.id_externo == id_externo).first()

            if time_existente:
                print(f"  Já existe: {nome} (id_externo={id_externo}) -> Time.id={time_existente.id}")
                ja_existiam += 1
                continue

            novo_time = Time(nome=nome, id_externo=id_externo, campeonato_id=campeonato.id)
            db.add(novo_time)
            db.commit()
            db.refresh(novo_time)

            print(f"  Criado: {nome} (id_externo={id_externo}) -> Time.id={novo_time.id}")
            criados += 1

        print(f"\nSincronização concluída. {criados} times criados, {ja_existiam} já existiam.")

    finally:
        db.close()


if __name__ == "__main__":
    sincronizar()