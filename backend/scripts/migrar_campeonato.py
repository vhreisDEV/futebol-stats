"""
Cria o modelo Campeonato de verdade e migra o Brasileirao (unico
campeonato que existe ate agora) pra usar ele -- primeiro passo pra
suportar multiplas ligas. So roda uma vez.

1. Cria a tabela `campeonatos` (Base.metadata.create_all so cria tabelas
   que ainda nao existem, nao mexe nas que ja existem).
2. Adiciona a coluna `campeonato_id` em `times` e `partidas` via ALTER
   TABLE (create_all nao adiciona coluna em tabela ja existente).
3. Insere a linha do Brasileirao Serie A 2026.
4. Faz o backfill: todo Time/Partida que ainda esta com campeonato_id
   NULL vira do Brasileirao (hoje e' o unico campeonato que existe, entao
   isso e' inequivoco).

Uso (de dentro de backend/):
    py scripts/migrar_campeonato.py
"""
from sqlalchemy import text

from app.database import Base, engine, SessionLocal
from app.models.time import Time  # noqa: F401 -- precisa estar importado para o relationship("Time") resolver
from app.models.partida import Partida  # noqa: F401 -- idem
from app.models.campeonato import Campeonato

LEAGUE_ID_BRASILEIRAO = 61205


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
    Base.metadata.create_all(bind=engine, tables=[Campeonato.__table__])
    print("Tabela 'campeonatos' garantida (criada se ainda nao existia).")

    with engine.connect() as conn:
        for tabela in ("times", "partidas"):
            if coluna_existe(conn, tabela, "campeonato_id"):
                print(f"Coluna campeonato_id ja existe em '{tabela}', pulando.")
                continue
            tipo_fk = "INTEGER REFERENCES campeonatos(id)"
            conn.execute(text(f"ALTER TABLE {tabela} ADD COLUMN campeonato_id {tipo_fk}"))
            conn.commit()
            print(f"Coluna campeonato_id adicionada em '{tabela}'.")

    db = SessionLocal()
    try:
        campeonato = db.query(Campeonato).filter(Campeonato.id_externo_liga == LEAGUE_ID_BRASILEIRAO).first()
        if not campeonato:
            campeonato = Campeonato(
                nome="Brasileirão Série A",
                pais_nome="Brasil",
                pais_codigo="BR",
                temporada=2026,
                id_externo_liga=LEAGUE_ID_BRASILEIRAO,
                rodadas_total=38,
                ativo=True,
            )
            db.add(campeonato)
            db.commit()
            db.refresh(campeonato)
            print(f"Campeonato criado: {campeonato.nome} (id={campeonato.id}).")
        else:
            print(f"Campeonato ja existia: {campeonato.nome} (id={campeonato.id}).")

        times_atualizados = (
            db.query(Time)
            .filter(Time.campeonato_id.is_(None))
            .update({"campeonato_id": campeonato.id})
        )
        partidas_atualizadas = (
            db.query(Partida)
            .filter(Partida.campeonato_id.is_(None))
            .update({"campeonato_id": campeonato.id})
        )
        db.commit()
        print(f"Backfill: {times_atualizados} times e {partidas_atualizadas} partidas vinculados ao Brasileirao.")
    finally:
        db.close()


if __name__ == "__main__":
    migrar()
