from datetime import date

from app.database import SessionLocal
from app.models.time import Time
from app.services.probabilidade_resultado import calcular_probabilidade_resultado


def main():
    db = SessionLocal()

    flamengo = db.query(Time).filter(Time.nome == "Flamengo").first()
    vitoria = db.query(Time).filter(Time.nome == "Vitoria").first()

    if not flamengo or not vitoria:
        print("Um dos times não foi encontrado no banco.")
        return

    data_referencia = date.today()

    print(f"Probabilidade de resultado: Flamengo (mandante) x Vitoria (visitante)")
    print(f"Data de referência: {data_referencia}\n")

    resultado = calcular_probabilidade_resultado(db, flamengo.id, vitoria.id, data_referencia)

    print(f"Vitória Flamengo: {resultado['probabilidade_vitoria_mandante']}%")
    print(f"Empate: {resultado['probabilidade_empate']}%")
    print(f"Vitória Vitoria: {resultado['probabilidade_vitoria_visitante']}%")

    print("\nDetalhe mandante:")
    print(resultado["detalhe_mandante"])

    print("\nDetalhe visitante:")
    print(resultado["detalhe_visitante"])

    db.close()


if __name__ == "__main__":
    main()