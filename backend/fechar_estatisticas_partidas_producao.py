# -*- coding: utf-8 -*-
"""
Execucao avulsa (2026-09-14, ver issue #49) pra fechar de uma vez o
passivo de 92 partidas finalizadas nas 5 ligas fora o Brasileirao que
nunca receberam estatistica agregada de partida (escanteios/chutes/
cartoes) -- bug corrigido no commit 8ff8421, mas so' daqui pra frente;
o historico so fecha reprocessando.

Diferente de importar_producao.py (que usa MAX_IMPORTACOES_POR_LIGA=20
pra nao deixar uma liga sozinha consumir a cota do dia todo), esse
script aqui da prioridade total a fechar o passivo: orcamento bem mais
alto por liga (so' o limite real da API por chamada de 429 que vai
parar o loop). Rodar UMA VEZ, de preferencia logo cedo com cota fresca,
antes do importar_jogadores_producao.py (que vai sobrar pouca ou
nenhuma cota nesse dia -- sem problema, atrasa so' 1 dia).

Uso (de dentro de backend/):
    py fechar_estatisticas_partidas_producao.py
"""
from dotenv import load_dotenv

load_dotenv(".env.production", override=True)

from app.database import SessionLocal  # noqa: E402
from app.models.campeonato import Campeonato  # noqa: E402
from scripts.importar_partidas import importar  # noqa: E402

MAX_IMPORTACOES_POR_LIGA = 100  # so' o 429 real vai frear isso, nao um cap artificial

if __name__ == "__main__":
    print("=== Fechando passivo de estatisticas de partida (issue #49) contra PRODUCAO (Supabase) ===\n")

    db = SessionLocal()
    campeonatos = (
        db.query(Campeonato)
        .filter(Campeonato.id_externo_liga.isnot(None))
        .order_by(Campeonato.id)
        .all()
    )
    db.close()

    for campeonato in campeonatos:
        print(f"\n----- {campeonato.nome} -----")
        resultado = importar(
            league_id=campeonato.id_externo_liga,
            season=campeonato.temporada,
            max_importacoes=MAX_IMPORTACOES_POR_LIGA,
        )
        if resultado and resultado.get("cota_excedida"):
            print("\nCota esgotada -- o que sobrar fica pra amanha (roda de novo, e' idempotente).")
            break

    print("\n=== Fim -- rode importar_jogadores_producao.py normalmente depois pra continuar o dia. ===")
