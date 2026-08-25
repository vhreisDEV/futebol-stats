# -*- coding: utf-8 -*-
"""
Roda scripts/corrigir_gols_penalti.py contra o banco de PRODUCAO
(Supabase). Mesmo principio do importar_producao.py -- ver esse arquivo
pra detalhes de por que o DATABASE_URL precisa ser carregado antes de
qualquer import de app.*.

Uso (de dentro de backend/):
    py corrigir_gols_penalti_producao.py --dry-run   # so mostra o que mudaria
    py corrigir_gols_penalti_producao.py             # aplica de verdade
"""
import sys

from dotenv import load_dotenv

load_dotenv(".env.production", override=True)

from scripts.corrigir_gols_penalti import corrigir  # noqa: E402

if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    print("=== Corrigindo gols de penalti contra PRODUCAO (Supabase) ===\n")
    corrigir(dry_run=dry_run)
