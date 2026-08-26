# -*- coding: utf-8 -*-
"""
Roda scripts/sincronizar_status_partidas.py contra o banco de PRODUCAO
(Supabase) -- mesmo principio do importar_producao.py. Barato (so'
listagem paginada de /matches, sem estatisticas), pensado pra rodar
todo dia antes de qualquer outro script gastar cota.

Uso (de dentro de backend/):
    py sincronizar_status_partidas_producao.py
"""
from dotenv import load_dotenv

load_dotenv(".env.production", override=True)

from scripts.sincronizar_status_partidas import sincronizar_todas  # noqa: E402

if __name__ == "__main__":
    print("=== Sincronizando status/placar de todas as ligas contra PRODUCAO (Supabase) ===\n")
    sincronizar_todas()
