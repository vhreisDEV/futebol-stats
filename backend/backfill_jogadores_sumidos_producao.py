# -*- coding: utf-8 -*-
"""
Roda scripts/backfill_jogadores_sumidos.py contra o banco de PRODUCAO
(Supabase) -- mesmo principio do importar_producao.py. So usa a API
publica do SofaScore (sem gastar cota da Highlightly).

Uso (de dentro de backend/):
    py backfill_jogadores_sumidos_producao.py <campeonato_id> [rodada]
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

load_dotenv(".env.production", override=True)

from scripts.backfill_jogadores_sumidos import backfill_liga  # noqa: E402

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: py backfill_jogadores_sumidos_producao.py <campeonato_id> [rodada]")
        sys.exit(1)
    campeonato_id_arg = int(sys.argv[1])
    rodada_arg = int(sys.argv[2]) if len(sys.argv) > 2 else None
    print(f"=== Backfill de jogadores sumidos contra PRODUCAO (Supabase), campeonato {campeonato_id_arg} ===\n")
    backfill_liga(campeonato_id_arg, rodada_arg)
