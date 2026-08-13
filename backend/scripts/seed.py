import random
from datetime import date, timedelta
from app.database import Base, engine, SessionLocal
from app.models.time import Time
from app.models.partida import Partida


def gerar_estatisticas_time():
    escanteios_1t = random.randint(1, 6)
    escanteios_2t = random.randint(1, 6)
    escanteios_total = escanteios_1t + escanteios_2t

    chutes_total = random.randint(5, 20)
    chutes_1t = random.randint(1, chutes_total)
    chutes_gol = random.randint(1, chutes_total)

    cartoes_amarelos = random.randint(0, 5)
    cartoes_vermelhos = random.choices([0, 1], weights=[9, 1])[0]

    gols = random.randint(0, 4)

    return {
        "gols": gols,
        "escanteios": escanteios_total,
        "escanteios_1t": escanteios_1t,
        "escanteios_2t": escanteios_2t,
        "chutes": chutes_total,
        "chutes_1t": chutes_1t,
        "chutes_gol": chutes_gol,
        "cartoes_amarelos": cartoes_amarelos,
        "cartoes_vermelhos": cartoes_vermelhos,
    }


def gerar_calendario(times, rodadas=10):
    pares = []
    for _ in range(rodadas):
        ids = [time.id for time in times]
        random.shuffle(ids)
        for i in range(0, len(ids), 2):
            pares.append((ids[i], ids[i + 1]))
    return pares


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(Time).count() > 0:
        print("Banco ja possui dados. Seed nao executado.")
        db.close()
        return

    flamengo = Time(nome="Flamengo")
    palmeiras = Time(nome="Palmeiras")
    botafogo = Time(nome="Botafogo")
    fluminense = Time(nome="Fluminense")

    db.add_all([flamengo, palmeiras, botafogo, fluminense])
    db.commit()

    times = [flamengo, palmeiras, botafogo, fluminense]
    pares = gerar_calendario(times, rodadas=10)

    partidas = []
    data_atual = date(2026, 8, 10)

    for time_mandante_id, time_visitante_id in pares:
        stats_mandante = gerar_estatisticas_time()
        stats_visitante = gerar_estatisticas_time()

        partidas.append(
            Partida(
                time_mandante_id=time_mandante_id,
                time_visitante_id=time_visitante_id,
                gols_mandante=stats_mandante["gols"],
                gols_visitante=stats_visitante["gols"],
                data=data_atual,
                escanteios_mandante=stats_mandante["escanteios"],
                escanteios_visitante=stats_visitante["escanteios"],
                escanteios_1t_mandante=stats_mandante["escanteios_1t"],
                escanteios_1t_visitante=stats_visitante["escanteios_1t"],
                escanteios_2t_mandante=stats_mandante["escanteios_2t"],
                escanteios_2t_visitante=stats_visitante["escanteios_2t"],
                chutes_mandante=stats_mandante["chutes"],
                chutes_visitante=stats_visitante["chutes"],
                chutes_1t_mandante=stats_mandante["chutes_1t"],
                chutes_1t_visitante=stats_visitante["chutes_1t"],
                chutes_gol_mandante=stats_mandante["chutes_gol"],
                chutes_gol_visitante=stats_visitante["chutes_gol"],
                cartoes_amarelos_mandante=stats_mandante["cartoes_amarelos"],
                cartoes_amarelos_visitante=stats_visitante["cartoes_amarelos"],
                cartoes_vermelhos_mandante=stats_mandante["cartoes_vermelhos"],
                cartoes_vermelhos_visitante=stats_visitante["cartoes_vermelhos"],
            )
        )
        data_atual -= timedelta(days=4)

    db.add_all(partidas)
    db.commit()
    db.close()

    print(f"Seed concluido com sucesso. {len(partidas)} partidas geradas.")


if __name__ == "__main__":
    seed()