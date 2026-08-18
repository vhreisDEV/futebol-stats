# -*- coding: utf-8 -*-
"""
Copia todos os dados reais do SQLite local (futebol_stats.db) pro
Postgres de producao, na ordem certa pra respeitar as foreign keys
(Time antes de Partida/Jogador, Jogador antes de
EstatisticaJogadorPartida). Roda uma vez, na primeira vez que o backend
for de fato pro Render -- evita ter que re-importar tudo da Highlightly
de novo (e gastar cota) so porque o banco trocou de SQLite pra Postgres.

Uso:
    py scripts/migrar_sqlite_para_postgres.py "postgresql://user:senha@host/db"

A URL do Postgres e a mesma que o Render mostra no dashboard do banco
(ou a env var DATABASE_URL que o proprio backend usa em producao).
"""
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, r"C:\Users\victorreis\futebol-stats\backend")

from app.database import Base
from app.models.time import Time
from app.models.partida import Partida
from app.models.jogador import Jogador
from app.models.estatistica_jogador_partida import EstatisticaJogadorPartida

SQLITE_URL = "sqlite:///./futebol_stats.db"

# Ordem importa: times/jogadores antes de quem referencia eles.
MODELOS_EM_ORDEM = [Time, Jogador, Partida, EstatisticaJogadorPartida]


def migrar(postgres_url):
    if postgres_url.startswith("postgres://"):
        postgres_url = postgres_url.replace("postgres://", "postgresql://", 1)

    origem = sessionmaker(bind=create_engine(SQLITE_URL))()
    destino_engine = create_engine(postgres_url)
    destino = sessionmaker(bind=destino_engine)()

    Base.metadata.create_all(bind=destino_engine)

    for Modelo in MODELOS_EM_ORDEM:
        ja_existe = destino.query(Modelo).count()
        if ja_existe:
            print(f"  {Modelo.__tablename__}: ja tem {ja_existe} linhas no destino, pulando (evita duplicar).")
            continue

        linhas = origem.query(Modelo).all()
        for linha in linhas:
            destino.merge(linha)
        destino.commit()
        print(f"  {Modelo.__tablename__}: {len(linhas)} linhas migradas.")

    origem.close()
    destino.close()
    print("\nMigracao concluida.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: py scripts/migrar_sqlite_para_postgres.py \"<postgres-url>\"")
        sys.exit(1)
    migrar(sys.argv[1])
