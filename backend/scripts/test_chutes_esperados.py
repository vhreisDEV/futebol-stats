from datetime import date

from app.database import SessionLocal
from app.models.time import Time
from app.services.chutes_esperados import calcular_chutes_esperados


def main():
    db = SessionLocal()

    flamengo = db.query(Time).filter(Time.nome == "Flamengo").first()
    vitoria = db.query(Time).filter(Time.nome == "Vitoria").first()

    if not flamengo or not vitoria:
        print("Um dos times não foi encontrado no banco.")
        return

    data_referencia = date.today()

    print(f"Chutes esperados: Flamengo (mandante) x Vitoria (visitante)")
    print(f"Data de referência: {data_referencia}\n")

    resultado = calcular_chutes_esperados(db, flamengo.id, vitoria.id, data_referencia)

    print(f"Chutes totais esperados Flamengo: {resultado['chutes_totais_esperados_mandante']}")
    print(f"Chutes totais esperados Vitoria: {resultado['chutes_totais_esperados_visitante']}")
    print(f"Chutes ao gol esperados Flamengo: {resultado['chutes_gol_esperados_mandante']}")
    print(f"Chutes ao gol esperados Vitoria: {resultado['chutes_gol_esperados_visitante']}")
    print(f"Chutes 1T esperados Flamengo: {resultado['chutes_1t_esperados_mandante']}")
    print(f"Chutes 1T esperados Vitoria: {resultado['chutes_1t_esperados_visitante']}")

    print("\nDetalhe chutes 1T mandante:")
    print(resultado["chutes_1t_detalhe_mandante"])

    print("\nDetalhe chutes 1T visitante:")
    print(resultado["chutes_1t_detalhe_visitante"])

    db.close()


if __name__ == "__main__":
    main()