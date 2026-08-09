from datetime import date
from app.database import Base, engine, SessionLocal
from app.models.time import Time
from app.models.partida import Partida

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

    partidas = [
        Partida(time_mandante_id=flamengo.id, time_visitante_id=palmeiras.id, gols_mandante=2, gols_visitante=1, data=date(2026, 7, 1)),
        Partida(time_mandante_id=botafogo.id, time_visitante_id=flamengo.id, gols_mandante=1, gols_visitante=0, data=date(2026, 7, 8)),
        Partida(time_mandante_id=flamengo.id, time_visitante_id=fluminense.id, gols_mandante=1, gols_visitante=1, data=date(2026, 7, 15)),
    ]

    db.add_all(partidas)
    db.commit()
    db.close()

    print("Seed concluido com sucesso.")

if __name__ == "__main__":
    seed()