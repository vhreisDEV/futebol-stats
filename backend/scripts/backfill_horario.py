"""
Preenche Partida.hora (campo novo, nunca existiu antes) pras partidas ja
importadas, e corrige Partida.data se a versao antiga (sem conversao BRT)
tiver deixado alguma errada. Reusa buscar_temporada_completa() -- lista a
temporada inteira em poucas requisicoes (nao uma por partida), entao isso
nao compete com a cota diaria dos imports normais. So atualiza partidas
que ja existem no banco (casadas por id_externo), nunca cria nada novo.

Uso (de dentro de backend/):
    py scripts/backfill_horario.py
"""
from app.database import SessionLocal
from app.models.time import Time  # noqa: F401 -- precisa estar importado pro relationship("Time") resolver
from app.models.partida import Partida
from scripts.importar_partidas import buscar_temporada_completa, parse_data_hora


def backfill():
    db = SessionLocal()
    try:
        partidas_api = buscar_temporada_completa()
        print(f"{len(partidas_api)} partidas na temporada (listagem completa).")

        atualizadas = 0
        datas_corrigidas = 0
        sem_correspondente = 0

        for p in partidas_api:
            id_externo = p["id"]
            partida = db.query(Partida).filter(Partida.id_externo == id_externo).first()
            if not partida:
                sem_correspondente += 1
                continue

            data_brt, hora_brt = parse_data_hora(p["date"])
            mudou = False

            if partida.hora != hora_brt:
                partida.hora = hora_brt
                mudou = True

            if partida.data != data_brt:
                print(f"  Corrigindo data: partida id={partida.id} rodada={partida.rodada} "
                      f"{partida.data} -> {data_brt}")
                partida.data = data_brt
                datas_corrigidas += 1
                mudou = True

            if mudou:
                atualizadas += 1

        db.commit()
        print(f"\nConcluido. {atualizadas} partidas atualizadas ({datas_corrigidas} com data corrigida), "
              f"{sem_correspondente} sem correspondente no banco.")
    finally:
        db.close()


if __name__ == "__main__":
    backfill()
