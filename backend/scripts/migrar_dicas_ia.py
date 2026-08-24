"""
Adiciona a coluna `dicas` em `analises_ia_partida` (paragrafo curto
sintetizando os mercados de "totais do jogo"). So roda uma vez.

Uso (de dentro de backend/):
    py scripts/migrar_dicas_ia.py
"""
from sqlalchemy import text

from app.database import engine


def coluna_existe(conn, tabela, coluna):
    dialeto = conn.engine.dialect.name
    if dialeto == "sqlite":
        linhas = conn.execute(text(f"PRAGMA table_info({tabela})")).fetchall()
        return any(linha[1] == coluna for linha in linhas)
    linha = conn.execute(
        text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = :tabela AND column_name = :coluna"
        ),
        {"tabela": tabela, "coluna": coluna},
    ).first()
    return linha is not None


def migrar():
    with engine.connect() as conn:
        if coluna_existe(conn, "analises_ia_partida", "dicas"):
            print("Coluna 'dicas' ja existe, pulando ALTER TABLE.")
        else:
            conn.execute(text("ALTER TABLE analises_ia_partida ADD COLUMN dicas VARCHAR"))
            conn.commit()
            print("Coluna 'dicas' adicionada.")


if __name__ == "__main__":
    migrar()
