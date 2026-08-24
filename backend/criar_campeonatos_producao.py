# -*- coding: utf-8 -*-
"""
Cria as linhas de Campeonato (Serie A e Ligue 1) contra o banco de
PRODUCAO (Supabase). So cria o registro do campeonato -- sync de
times/partidas fica pra depois, via os scripts de import de sempre.

Uso (de dentro de backend/):
    py criar_campeonatos_producao.py
"""
from dotenv import load_dotenv

load_dotenv(".env.production", override=True)

from app.database import SessionLocal  # noqa: E402
from scripts.criar_campeonato import criar_campeonato  # noqa: E402

if __name__ == "__main__":
    print("=== Criando campeonatos contra PRODUCAO (Supabase) ===\n")
    db = SessionLocal()
    try:
        criar_campeonato(db, 115669)  # Serie A (Italia)
        criar_campeonato(db, 52695)  # Ligue 1 (Franca)
    finally:
        db.close()
