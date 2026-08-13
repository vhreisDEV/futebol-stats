from datetime import date

from app.database import SessionLocal
from app.models.time import Time
from app.services.escanteios_esperados import calcular_escanteios_esperados


def main():
    db = SessionLocal()

    flamengo = db.query(Time).filter(Time.nome == "Flamengo").first()
    vitoria = db.query(Time).filter(Time.nome == "Vitoria").first()

    if not flamengo or not vitoria:
        print("Um dos times não foi encontrado no banco.")
        return

    data_referencia = date.today()

    print(f"Escanteios esperados: Flamengo (mandante) x Vitoria (visitante)")
    print(f"Data de referência: {data_referencia}\n")

    resultado = calcular_escanteios_esperados(db, flamengo.id, vitoria.id, data_referencia)

    print(f"Escanteios esperados Flamengo: {resultado['escanteios_esperados_mandante']}")
    print(f"Escanteios esperados Vitoria: {resultado['escanteios_esperados_visitante']}")
    print(f"Total esperado: {resultado['total_esperado']}")
    print(f"Tendência (linha {resultado['linha_referencia']}): {resultado['tendencia']}")

    print("\nDetalhe mandante:")
    print(resultado["detalhe_mandante"])

    print("\nDetalhe visitante:")
    print(resultado["detalhe_visitante"])

    db.close()


if __name__ == "__main__":
    main()