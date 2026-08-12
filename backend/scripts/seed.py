import random
from datetime import date
from app.database import Base, engine, SessionLocal
from app.models.time import Time
from app.models.partida import Partida


def gerar_estatisticas_time():
    escanteios_1t = random.randint(1, 6)
    escanteios_2t = random.randint(1, 6)
    escanteios_total = escanteios_1t + escanteios_2t

    chutes_total = random.randint(5, 20)
    chutes_gol = random.randint(1, chutes_total)

    cartoes_amarelos = random.randint(0, 5)
    cartoes_vermelhos = random.choices([0, 1], weights=[9, 1])[0]

    return {
        "escanteios": escanteios_total,
        "escanteios_1t": escanteios_1t,
        "escanteios_2t": escanteios_2t,
        "chutes": chutes_total,
        "chutes_gol": chutes_gol,
        "cartoes_amarelos": cartoes_amarelos,
        "cartoes_vermelhos": cartoes_vermelhos,
    }


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

    jogos_base = [
        (flamengo.id, palmeiras.id, 2, 1, date(2026, 7, 1)),
        (botafogo.id, flamengo.id, 1, 0, date(2026, 7, 8)),
        (flamengo.id, fluminense.id, 1, 1, date(2026, 7, 15)),
    ]

    partidas = []
    for time_mandante_id, time_visitante_id, gols_mandante, gols_visitante, data_jogo in jogos_base:
        stats_mandante = gerar_estatisticas_time()
        stats_visitante = gerar_estatisticas_time()

        partidas.append(
            Partida(
                time_mandante_id=time_mandante_id,
                time_visitante_id=time_visitante_id,
                gols_mandante=gols_mandante,
                gols_visitante=gols_visitante,
                data=data_jogo,
                escanteios_mandante=stats_mandante["escanteios"],
                escanteios_visitante=stats_visitante["escanteios"],
                escanteios_1t_mandante=stats_mandante["escanteios_1t"],
                escanteios_1t_visitante=stats_visitante["escanteios_1t"],
                escanteios_2t_mandante=stats_mandante["escanteios_2t"],
                escanteios_2t_visitante=stats_visitante["escanteios_2t"],
                chutes_mandante=stats_mandante["chutes"],
                chutes_visitante=stats_visitante["chutes"],
                chutes_gol_mandante=stats_mandante["chutes_gol"],
                chutes_gol_visitante=stats_visitante["chutes_gol"],
                cartoes_amarelos_mandante=stats_mandante["cartoes_amarelos"],
                cartoes_amarelos_visitante=stats_visitante["cartoes_amarelos"],
                cartoes_vermelhos_mandante=stats_mandante["cartoes_vermelhos"],
                cartoes_vermelhos_visitante=stats_visitante["cartoes_vermelhos"],
            )
        )

    db.add_all(partidas)
    db.commit()
    db.close()

    print("Seed concluido com sucesso.")


if __name__ == "__main__":
    seed()