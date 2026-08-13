from app.database import SessionLocal
from app.models.time import Time
from app.models.partida import Partida


def main():
    db = SessionLocal()

    partidas_ficticias = db.query(Partida).filter(Partida.id_externo.is_(None)).all()

    print(f"{len(partidas_ficticias)} partidas fictícias encontradas (sem id_externo).")

    if not partidas_ficticias:
        print("Nada para remover.")
        db.close()
        return

    for p in partidas_ficticias:
        print(f"  Removendo: Partida.id={p.id}, data={p.data}, "
              f"mandante_id={p.time_mandante_id}, visitante_id={p.time_visitante_id}")
        db.delete(p)

    db.commit()

    restantes = db.query(Partida).count()
    print(f"\nRemoção concluída. {restantes} partidas restantes no banco (todas reais, com id_externo).")

    db.close()


if __name__ == "__main__":
    main()