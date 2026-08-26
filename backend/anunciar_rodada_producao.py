# -*- coding: utf-8 -*-
"""
Roda scripts/anunciar_rodada.py contra o banco de PRODUCAO (Supabase) e
manda o aviso pros inscritos reais do Telegram.

Uso (de dentro de backend/):
    py anunciar_rodada_producao.py 25
"""
import sys

from dotenv import load_dotenv

load_dotenv(".env.production", override=True)

from scripts.anunciar_rodada import anunciar_rodada  # noqa: E402

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: py anunciar_rodada_producao.py <numero_da_rodada> [--dry-run]")
        sys.exit(1)
    anunciar_rodada(campeonato_id=1, numero_rodada=int(sys.argv[1]), dry_run="--dry-run" in sys.argv)
