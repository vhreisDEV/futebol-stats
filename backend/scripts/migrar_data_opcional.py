"""
Migracao unica: torna Partida.data opcional (agora que vamos cadastrar
confrontos de rodadas futuras sem data/hora oficial ainda definida pela
CBF). Mesmo procedimento de migrar_status_partida.py -- SQLite nao
suporta ALTER COLUMN pra remover NOT NULL, entao recria a tabela.
"""

import sqlite3
from app.database import engine
from app.models.time import Time  # noqa: F401 -- FK de Partida precisa disso resolvido
from app.models.partida import Partida  # schema ja atualizado

DB_PATH = "futebol_stats.db"

COLUNAS = [
    "id", "id_externo", "time_mandante_id", "time_visitante_id", "status",
    "data", "rodada",
    "gols_mandante", "gols_visitante",
    "escanteios_mandante", "escanteios_visitante",
    "escanteios_1t_mandante", "escanteios_1t_visitante",
    "escanteios_2t_mandante", "escanteios_2t_visitante",
    "chutes_mandante", "chutes_visitante",
    "chutes_1t_mandante", "chutes_1t_visitante",
    "chutes_gol_mandante", "chutes_gol_visitante",
    "cartoes_amarelos_mandante", "cartoes_amarelos_visitante",
    "cartoes_vermelhos_mandante", "cartoes_vermelhos_visitante",
]


def _tabela_existe(cur, nome):
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (nome,))
    return cur.fetchone() is not None


def migrar():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    ja_renomeada = _tabela_existe(cur, "partidas_old")

    if _tabela_existe(cur, "partidas") and not ja_renomeada:
        cur.execute("PRAGMA table_info(partidas)")
        info = {r[1]: r[3] for r in cur.fetchall()}  # nome -> notnull (1/0)
        if info.get("data") == 0:
            print("Coluna data ja e opcional -- migracao ja foi aplicada.")
            conn.close()
            return

        total_antes = cur.execute("SELECT COUNT(*) FROM partidas").fetchone()[0]
        print(f"{total_antes} partidas na tabela atual.")

        cur.execute("ALTER TABLE partidas RENAME TO partidas_old")
        conn.commit()
    elif ja_renomeada:
        total_antes = cur.execute("SELECT COUNT(*) FROM partidas_old").fetchone()[0]
        print(f"Retomando migracao interrompida -- {total_antes} partidas em partidas_old.")
    else:
        print("Tabela partidas nao existe -- nada a migrar.")
        conn.close()
        return

    conn_check = sqlite3.connect(DB_PATH)
    cur_check = conn_check.cursor()
    partidas_ja_criada = _tabela_existe(cur_check, "partidas")

    if not partidas_ja_criada:
        cur_check.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='partidas_old' "
            "AND name NOT LIKE 'sqlite_autoindex%'"
        )
        for (nome_indice,) in cur_check.fetchall():
            cur_check.execute(f"DROP INDEX {nome_indice}")
        conn_check.commit()

    conn_check.close()
    conn.close()

    if not partidas_ja_criada:
        Partida.__table__.create(bind=engine)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    colunas_str = ", ".join(COLUNAS)
    cur.execute(f"INSERT INTO partidas ({colunas_str}) SELECT {colunas_str} FROM partidas_old")
    conn.commit()

    total_depois = cur.execute("SELECT COUNT(*) FROM partidas").fetchone()[0]
    print(f"{total_depois} partidas copiadas para a tabela nova.")

    if total_depois != total_antes:
        conn.close()
        raise RuntimeError(
            f"Contagem nao bate ({total_antes} -> {total_depois}). "
            "Tabela partidas_old preservada -- investigue antes de rodar de novo."
        )

    cur.execute("DROP TABLE partidas_old")
    conn.commit()
    conn.close()

    print("Migracao concluida: Partida.data agora e opcional.")


if __name__ == "__main__":
    migrar()
