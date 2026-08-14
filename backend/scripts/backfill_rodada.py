import requests

from app.database import SessionLocal
from app.models.partida import Partida
from scripts.importar_partidas import API_KEY, buscar_detalhe_partida, parse_rodada


def backfill():
    if not API_KEY:
        print("ERRO: HIGHLIGHTLY_API_KEY não encontrada no .env")
        return

    db = SessionLocal()
    atualizadas = 0
    sem_round = 0

    try:
        partidas = (
            db.query(Partida)
            .filter(Partida.rodada.is_(None), Partida.id_externo.isnot(None))
            .all()
        )

        print(f"{len(partidas)} partidas sem rodada para preencher.\n")

        for partida in partidas:
            try:
                detalhe = buscar_detalhe_partida(partida.id_externo)
            except requests.exceptions.HTTPError as e:
                if e.response is not None and e.response.status_code == 429:
                    print(f"\nCota da Highlightly esgotada. Pare e rode de novo depois. "
                          f"({atualizadas} atualizadas até agora)")
                    break
                print(f"  Erro ao buscar partida {partida.id_externo}: {e}")
                continue

            if not detalhe:
                print(f"  Pulando partida {partida.id_externo}: detalhe não encontrado")
                continue

            rodada = parse_rodada(detalhe.get("round"))
            if rodada is None:
                print(f"  Partida {partida.id_externo}: campo 'round' ausente/inesperado "
                      f"({detalhe.get('round')!r})")
                sem_round += 1
                continue

            partida.rodada = rodada
            db.commit()
            print(f"  Partida {partida.id_externo}: rodada {rodada}")
            atualizadas += 1

        print(f"\nBackfill concluído. {atualizadas} partidas atualizadas, {sem_round} sem rodada identificada.")

    finally:
        db.close()


if __name__ == "__main__":
    backfill()
