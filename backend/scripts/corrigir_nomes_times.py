from app.database import SessionLocal
from app.models.time import Time

# Nomes como a Highlightly retorna -> nome oficial da Serie A que queremos exibir
CORRECOES = {
    "Athletico Paranaense": "Athletico-PR",
    "Atletico-MG": "Atlético-MG",
    "Gremio": "Grêmio",
    "RB Bragantino": "Red Bull Bragantino",
    "São Paulo FC": "São Paulo",
    "Vasco DA Gama": "Vasco da Gama",
    "Vitoria": "Vitória",
}


def corrigir():
    db = SessionLocal()
    corrigidos = 0

    try:
        for nome_atual, nome_correto in CORRECOES.items():
            time = db.query(Time).filter(Time.nome == nome_atual).first()
            if not time:
                print(f"  Não encontrado (já corrigido ou nome mudou): {nome_atual!r}")
                continue

            time.nome = nome_correto
            db.commit()
            print(f"  Corrigido: {nome_atual!r} -> {nome_correto!r}")
            corrigidos += 1

        print(f"\n{corrigidos} times corrigidos.")

    finally:
        db.close()


if __name__ == "__main__":
    corrigir()
