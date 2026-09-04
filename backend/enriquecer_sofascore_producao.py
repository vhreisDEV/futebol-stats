# -*- coding: utf-8 -*-
"""
Roda scripts/enriquecer_sofascore.py contra o banco de PRODUCAO
(Supabase), mesmo principio do importar_producao.py.

Uso (de dentro de backend/):
    py enriquecer_sofascore_producao.py <campeonato_id> <rodada>
"""
import sys

from dotenv import load_dotenv

load_dotenv(".env.production", override=True)

from scripts.enriquecer_sofascore import enriquecer_rodada  # noqa: E402

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: py enriquecer_sofascore_producao.py <campeonato_id> <numero_da_rodada>")
        sys.exit(1)
    print("=== Enriquecendo com SofaScore contra PRODUCAO (Supabase) ===\n")
    enriquecer_rodada(int(sys.argv[1]), int(sys.argv[2]))
