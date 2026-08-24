"""
Corrige sequences de PK dessincronizadas no Postgres -- acontece quando uma
tabela e' populada via session.merge() com id explicito (como
migrar_sqlite_para_postgres.py faz), que preserva os IDs mas nao avanca a
sequence de autoincremento. O sintoma so aparece na primeira vez que
alguem tenta inserir uma linha nova de verdade nessa tabela via ORM: da
IntegrityError "duplicate key value violates unique constraint" porque a
sequence ainda esta tentando reusar um id que ja existe.

Achado e corrigido em producao 2026-08-24 nas tabelas times e partidas
(ambas populadas via merge() na migracao inicial pro Supabase e nunca
mais tinham recebido uma linha nova de verdade ate a importacao da
Premier League estourar o erro). jogadores e estatisticas_jogador_partida
ja estavam ok (populadas via insert normal desde o inicio, nunca via
merge).

So funciona contra Postgres -- SQLite nao usa sequence, e' rowid direto.

Uso (de dentro de backend/):
    py scripts/corrigir_sequences_postgres.py tabela1 tabela2 ...
"""
import sys

from app.database import engine
from sqlalchemy import text


def verificar_e_corrigir(tabela, aplicar=True):
    with engine.connect() as conn:
        seq = conn.execute(text(f"SELECT pg_get_serial_sequence('{tabela}', 'id')")).scalar()
        if not seq:
            print(f"{tabela}: sem sequence (coluna id nao e' serial?), pulando.")
            return

        maxid = conn.execute(text(f"SELECT COALESCE(MAX(id), 0) FROM {tabela}")).scalar()
        atual = conn.execute(text(f"SELECT last_value FROM {seq}")).scalar()

        if atual >= maxid:
            print(f"{tabela}: OK (sequence={atual}, max(id)={maxid}).")
            return

        print(f"{tabela}: DESSINCRONIZADA (sequence={atual}, max(id)={maxid}).")
        if aplicar:
            conn.execute(text(f"SELECT setval('{seq}', {maxid})"))
            conn.commit()
            print(f"  Corrigido: sequence agora em {maxid}.")


if __name__ == "__main__":
    tabelas = sys.argv[1:] or ["times", "partidas", "jogadores", "estatisticas_jogador_partida", "campeonatos"]
    for tabela in tabelas:
        verificar_e_corrigir(tabela)
