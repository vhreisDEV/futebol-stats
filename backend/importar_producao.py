# -*- coding: utf-8 -*-
"""
Roda o import real da Highlightly contra o banco de PRODUCAO (Supabase),
nao o SQLite local usado no dia a dia de desenvolvimento.

Uso (de dentro de backend/):
    py importar_producao.py

Precisa do arquivo .env.production (nao versionado) com a linha:
    DATABASE_URL=postgresql://...  <- connection string do Supabase

O DATABASE_URL precisa ser carregado ANTES de qualquer import de app.*,
porque app/database.py le a variavel de ambiente no momento em que o
modulo e importado, nao em runtime.
"""
from dotenv import load_dotenv

load_dotenv(".env.production", override=True)

from scripts.importar_partidas import importar  # noqa: E402 -- import atrasado de proposito, ver acima

if __name__ == "__main__":
    print("=== Rodando import contra PRODUCAO (Supabase) ===\n")
    importar()
