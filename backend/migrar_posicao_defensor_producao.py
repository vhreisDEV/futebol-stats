# -*- coding: utf-8 -*-
"""
Roda scripts/migrar_posicao_defensor.py contra o banco de PRODUCAO
(Supabase).

Uso (de dentro de backend/):
    py migrar_posicao_defensor_producao.py
"""
from dotenv import load_dotenv

load_dotenv(".env.production", override=True)

from scripts.migrar_posicao_defensor import migrar  # noqa: E402

if __name__ == "__main__":
    print("=== Migrando posicao 'Zagueiro' -> 'Defensor' em PRODUCAO (Supabase) ===\n")
    migrar()
