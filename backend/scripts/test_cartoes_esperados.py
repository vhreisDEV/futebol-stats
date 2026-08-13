from datetime import date

from app.database import SessionLocal
from app.models.time import Time
from app.services.cartoes_esperados import calcular_cartoes_esperados


def main():
    db = SessionLocal()

    flamengo = db.query(Time).filter(Time.nome == "Flamengo").first()
    vitoria = db.query(Time).filter(Time.nome == "Vitoria").first()

    if not flamengo or not vitoria:
        print("Um dos times não foi encontrado no banco.")
        return

    data_referencia = date.today()

    print(f"Cartões esperados: Flamengo (mandante) x Vitoria (visitante)")
    print(f"Data de referência: {data_referencia}\n")

    resultado = calcular_cartoes_esperados(db, flamengo.id, vitoria.id, data_referencia)

    print(f"Cartões amarelos esperados Flamengo: {resultado['cartoes_amarelos_esperados_mandante']}")
    print(f"Cartões amarelos esperados Vitoria: {resultado['cartoes_amarelos_esperados_visitante']}")
    print(f"Cartões vermelhos esperados Flamengo: {resultado['cartoes_vermelhos_esperados_mandante']}")
    print(f"Cartões vermelhos esperados Vitoria: {resultado['cartoes_vermelhos_esperados_visitante']}")
    print(f"Total de cartões esperado na partida: {resultado['total_cartoes_esperado']}")

    db.close()


if __name__ == "__main__":
    main()
