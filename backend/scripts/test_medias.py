from datetime import date

from app.database import SessionLocal
from app.models.time import Time
from app.services.medias import calcular_medias, calcular_medias_completas


def main():
    db = SessionLocal()

    flamengo = db.query(Time).filter(Time.nome == "Flamengo").first()
    if not flamengo:
        print("Time 'Flamengo' não encontrado no banco.")
        return

    data_referencia = date.today()

    print(f"Médias do Flamengo (Time.id={flamengo.id}), referência: {data_referencia}\n")

    print("Janela de 5 jogos, geral:")
    print(calcular_medias(db, flamengo.id, data_referencia, janela=5, mando=None))

    print("\nJanela de 5 jogos, como mandante:")
    print(calcular_medias(db, flamengo.id, data_referencia, janela=5, mando="mandante"))

    print("\nJanela de 10 jogos, geral:")
    print(calcular_medias(db, flamengo.id, data_referencia, janela=10, mando=None))

    print("\nTodas as combinações de uma vez:")
    completas = calcular_medias_completas(db, flamengo.id, data_referencia)
    for chave, valores in completas.items():
        print(f"  {chave}: {valores}")

    db.close()


if __name__ == "__main__":
    main()
