"""
Adiciona a coluna `nome` em `telegram_subscribers` (primeiro nome que o
Telegram manda junto do /start, usado pra personalizar a mensagem de
boas-vindas e os broadcasts). So roda uma vez.

Uso (de dentro de backend/):
    py scripts/migrar_telegram_nome.py
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
        if coluna_existe(conn, "telegram_subscribers", "nome"):
            print("Coluna 'nome' ja existe, pulando ALTER TABLE.")
            return
        conn.execute(text("ALTER TABLE telegram_subscribers ADD COLUMN nome VARCHAR"))
        conn.commit()
        print("Coluna 'nome' adicionada.")


if __name__ == "__main__":
    migrar()
