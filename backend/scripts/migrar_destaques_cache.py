"""
Adiciona em `analises_ia_partida` as colunas usadas pra cachear os
destaques/bilhetes ja calculados (destaques_json, mandante_ultimo_jogo,
visitante_ultimo_jogo) -- antes so o texto da IA era cacheado, o resto
era recalculado (varias queries) a cada abertura da pagina. So roda uma
vez.

Uso (de dentro de backend/):
    py scripts/migrar_destaques_cache.py
"""
from sqlalchemy import text

from app.database import engine

COLUNAS = {
    "destaques_json": "TEXT",
    "mandante_ultimo_jogo": "DATE",
    "visitante_ultimo_jogo": "DATE",
}


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
        for coluna, tipo in COLUNAS.items():
            if coluna_existe(conn, "analises_ia_partida", coluna):
                print(f"Coluna '{coluna}' ja existe, pulando ALTER TABLE.")
                continue
            conn.execute(text(f"ALTER TABLE analises_ia_partida ADD COLUMN {coluna} {tipo}"))
            conn.commit()
            print(f"Coluna '{coluna}' adicionada.")


if __name__ == "__main__":
    migrar()
