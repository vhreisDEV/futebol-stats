# -*- coding: utf-8 -*-
"""
Roda o import de jogadores (gols/assistencias/cartoes via lineups+events)
contra o banco de PRODUCAO (Supabase). Mesmo principio do
importar_producao.py -- ver esse arquivo pra detalhes de por que o
DATABASE_URL precisa ser carregado antes de qualquer import de app.*.

Uso (de dentro de backend/):
    py importar_jogadores_producao.py
"""
from dotenv import load_dotenv

load_dotenv(".env.production", override=True)

from scripts.importar_jogadores import importar_jogadores  # noqa: E402

if __name__ == "__main__":
    print("=== Rodando import de jogadores contra PRODUCAO (Supabase) ===\n")
    importar_jogadores()
