# -*- coding: utf-8 -*-
"""
Roda scripts/notificar_telegram.py contra o banco de PRODUCAO (Supabase)
-- os inscritos reais estao la, nao no SQLite local. Mesmo principio do
importar_producao.py.

Uso (de dentro de backend/):
    py notificar_telegram_producao.py "Rodada 25 liberada! https://veaga-psi.vercel.app"
"""
import sys

from dotenv import load_dotenv

load_dotenv(".env.production", override=True)

from scripts.notificar_telegram import notificar  # noqa: E402

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Uso: py notificar_telegram_producao.py "texto da mensagem"')
        sys.exit(1)
    notificar(sys.argv[1])
