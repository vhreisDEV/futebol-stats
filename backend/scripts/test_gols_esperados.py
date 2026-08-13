from datetime import date

from app.database import SessionLocal
from app.models.time import Time
from app.services.gols_esperados import calcular_gols_esperados


def main():
    db = SessionLocal()

    flamengo = db.query(Time).filter(Time.nome == "Flamengo").first()
    vitoria = db.query(Time).filter(Time.nome == "Vitoria").first()

    if not flamengo or not vitoria:
        print("Um dos times não foi encontrado no banco.")
        return

    data_referencia = date.today()

    print(f"Gols esperados: Flamengo (mandante) x Vitoria (visitante)")
    print(f"Data de referência: {data_referencia}\n")

    resultado = calcular_gols_esperados(db, flamengo.id, vitoria.id, data_referencia)

    print(f"Gols esperados mandante (Flamengo): {resultado['gols_esperados_mandante']}")
    print(f"Gols esperados visitante (Vitoria): {resultado['gols_esperados_visitante']}")

    if resultado.get("gols_esperados_mandante") is not None:
        print(f"\nJanela usada: {resultado['janela_usada']}")

    print("\nDetalhe mandante:")
    print(resultado["detalhe_mandante"])

    print("\nDetalhe visitante:")
    print(resultado["detalhe_visitante"])

    db.close()


if __name__ == "__main__":
    main()