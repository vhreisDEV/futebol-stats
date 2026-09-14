# -*- coding: utf-8 -*-
"""
Roda o import real da Highlightly contra o banco de PRODUCAO (Supabase),
nao o SQLite local usado no dia a dia de desenvolvimento.

Ate 2026-09-14 esse script so importava estatisticas de partida
(escanteios/chutes/cartoes) do Brasileirao -- scripts/importar_partidas.py
tinha o league_id do Brasileirao como default e nunca era chamado com
outro. As outras 5 ligas so recebiam status/placar (via
sincronizar_status_partidas_producao.py) e estatistica POR JOGADOR (via
importar_jogadores_producao.py + SofaScore), nunca a estatistica
agregada da propria partida -- ficavam com escanteios/chutes/cartoes
NULL pra sempre. Generalizado aqui pra rodar em todas as ligas
cadastradas, uma de cada vez, com orcamento de chamadas dividido entre
elas (a cota de 100/dia e' da API inteira, compartilhada -- nao faz
sentido deixar soh o Brasileirao consumir tudo antes das outras ligas
serem tentadas).

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

from app.database import SessionLocal  # noqa: E402
from app.models.campeonato import Campeonato  # noqa: E402
from scripts.importar_partidas import importar  # noqa: E402 -- import atrasado de proposito, ver acima

MAX_IMPORTACOES_POR_LIGA = 20  # 6 ligas * 20 ~ orcamento parecido com o cap antigo (90) so' pro Brasileirao

if __name__ == "__main__":
    print("=== Rodando import contra PRODUCAO (Supabase) ===\n")

    db = SessionLocal()
    campeonatos = (
        db.query(Campeonato)
        .filter(Campeonato.id_externo_liga.isnot(None))
        .order_by(Campeonato.id)
        .all()
    )
    db.close()

    for campeonato in campeonatos:
        print(f"\n----- {campeonato.nome} -----")
        resultado = importar(
            league_id=campeonato.id_externo_liga,
            season=campeonato.temporada,
            max_importacoes=MAX_IMPORTACOES_POR_LIGA,
        )
        if resultado and resultado.get("cota_excedida"):
            print("\nCota esgotada -- parando por aqui, as ligas restantes ficam pra amanha.")
            break
