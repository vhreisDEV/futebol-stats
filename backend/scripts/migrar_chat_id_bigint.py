"""
Corrige o tipo da coluna `telegram_subscribers.chat_id` de INTEGER pra
BIGINT -- contas novas do Telegram tem id maior que o limite de um
Integer comum (2.147.483.647), causando overflow ao gravar no Postgres
de producao. So roda uma vez (idempotente).

Uso (de dentro de backend/):
    py scripts/migrar_chat_id_bigint.py
"""
from sqlalchemy import text

from app.database import engine


def migrar():
    with engine.connect() as conn:
        dialeto = conn.engine.dialect.name
        if dialeto == "sqlite":
            print("SQLite nao reforca largura de INTEGER -- nada a fazer localmente.")
            return
        conn.execute(text("ALTER TABLE telegram_subscribers ALTER COLUMN chat_id TYPE BIGINT"))
        conn.commit()
        print("Coluna 'chat_id' migrada pra BIGINT.")


if __name__ == "__main__":
    migrar()
