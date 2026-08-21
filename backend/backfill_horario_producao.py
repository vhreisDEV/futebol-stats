# -*- coding: utf-8 -*-
"""
Roda o backfill de horario contra o banco de PRODUCAO (Supabase). Mesmo
principio do importar_producao.py -- DATABASE_URL precisa ser carregado
antes de qualquer import de app.*.

Uso (de dentro de backend/):
    py backfill_horario_producao.py
"""
from dotenv import load_dotenv

load_dotenv(".env.production", override=True)

from scripts.backfill_horario import backfill  # noqa: E402

if __name__ == "__main__":
    print("=== Rodando backfill de horario contra PRODUCAO (Supabase) ===\n")
    backfill()
