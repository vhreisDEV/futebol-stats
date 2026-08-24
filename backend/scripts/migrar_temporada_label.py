"""
Adiciona Campeonato.temporada_label (rotulo de exibicao, ex.: "2026" pro
Brasileirao vs "2026-27" pras ligas europeias que atravessam dois anos
civis) e faz o backfill dos campeonatos ja existentes. So roda uma vez.

Uso (de dentro de backend/):
    py scripts/migrar_temporada_label.py
"""
from sqlalchemy import text

from app.database import engine, SessionLocal
from app.models.campeonato import Campeonato
from scripts.criar_campeonato import CAMPEONATOS_CONHECIDOS, montar_temporada_label


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
        if coluna_existe(conn, "campeonatos", "temporada_label"):
            print("Coluna temporada_label ja existe, pulando ALTER TABLE.")
        else:
            conn.execute(text("ALTER TABLE campeonatos ADD COLUMN temporada_label VARCHAR"))
            conn.commit()
            print("Coluna temporada_label adicionada.")

    db = SessionLocal()
    try:
        atualizados = 0
        for campeonato in db.query(Campeonato).all():
            if campeonato.temporada_label:
                continue

            if campeonato.pais_codigo == "BR":
                label = str(campeonato.temporada)
            else:
                info = CAMPEONATOS_CONHECIDOS.get(campeonato.id_externo_liga)
                temporada_dupla = info["temporada_dupla"] if info else True
                label = montar_temporada_label(campeonato.temporada, temporada_dupla)

            campeonato.temporada_label = label
            atualizados += 1
            print(f"  {campeonato.nome}: temporada_label = {label}")

        db.commit()
        print(f"\nConcluido. {atualizados} campeonatos atualizados.")
    finally:
        db.close()


if __name__ == "__main__":
    migrar()
