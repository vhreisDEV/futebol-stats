# -*- coding: utf-8 -*-
"""
Backfill dos jogadores "sumidos" (issue #48): jogaram de verdade
(confirmado pelo SofaScore, minutesPlayed preenchido) mas nunca
ganharam uma linha em EstatisticaJogadorPartida porque a Highlightly
nao registrou nenhum evento de substituicao pra eles (so listava como
reserva no /lineups, sem o evento correspondente no /events -- causa
raiz confirmada em 85% de uma amostra de 74 partidas, ver issue #48).

So cria linha pra jogador que JA EXISTE no nosso elenco daquele time
(nunca cria Jogador novo a partir do SofaScore sozinho -- mesma
restricao de enriquecer_sofascore.py). Se nao achar por interseccao de
nome (casar_jogador), reporta e pula -- nao adivinha.

gols/assistencias vem do SofaScore ("goals"/"goalAssist" na
estatistica do jogador) porque aqui nao ha nenhum evento da Highlightly
pra essa linha (diferente de enriquecer_sofascore.py, que so enriquece
campo ja None de uma linha que a Highlightly ja criou). cartoes ficam
0 -- o SofaScore nao expoe cartao no payload por jogador (so' via
/incidents, fora de escopo por ora).

Idempotente: nunca cria linha duplicada pro mesmo jogador+partida,
seguro rodar de novo.

Uso (de dentro de backend/; local usa SQLite, ver
backfill_jogadores_sumidos_producao.py pra producao):
    py scripts/backfill_jogadores_sumidos.py <campeonato_id>
    py scripts/backfill_jogadores_sumidos.py <campeonato_id> <rodada>
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.campeonato import Campeonato
from app.models.jogador import Jogador
from app.models.partida import Partida
from app.models.estatistica_jogador_partida import EstatisticaJogadorPartida
from scripts.enriquecer_sofascore import (
    CONFIG_LIGA, MAPA_CAMPOS, buscar_eventos_rodada, encontrar_evento,
    buscar_lineups, casar_jogador,
)


def backfill_partida(db, partida, evento_sofascore):
    """Cria linha de EstatisticaJogadorPartida pra quem jogou de verdade
    (confirmado pelo SofaScore) mas ainda nao tem linha nenhuma nossa.
    Devolve (criadas, nao_casados) -- nao_casados e' lista de nomes que
    o SofaScore confirma terem jogado mas nao bateram com ninguem do
    elenco atual do time (pode ser jogador transferido depois dessa
    partida, mesma limitacao ja documentada em enriquecer_sofascore.py,
    nao e' necessariamente bug)."""
    lineups = buscar_lineups(evento_sofascore["id"])
    if not lineups:
        return 0, []

    criadas = 0
    nao_casados = []

    for lado, time_id_nosso in (("home", partida.time_mandante_id), ("away", partida.time_visitante_id)):
        linhas_existentes = {
            row[0]
            for row in db.query(EstatisticaJogadorPartida.jogador_id)
            .filter(
                EstatisticaJogadorPartida.partida_id == partida.id,
                EstatisticaJogadorPartida.time_id == time_id_nosso,
            )
            .all()
        }
        elenco_time = db.query(Jogador).filter(Jogador.time_id == time_id_nosso).all()

        for entrada in lineups.get(lado, {}).get("players", []):
            stats_sofa = entrada.get("statistics") or {}
            if stats_sofa.get("minutesPlayed") is None:
                continue  # nao jogou, nao e' "sumido"

            jogador = casar_jogador(entrada["player"]["name"], elenco_time)
            if not jogador:
                nao_casados.append(entrada["player"]["name"])
                continue
            if jogador.id in linhas_existentes:
                continue  # ja tem linha (Highlightly ou backfill anterior)

            # mesma regra de enriquecer_sofascore.py: jogou de verdade
            # (minutesPlayed presente) + chave ausente = zero de
            # verdade, nao dado faltando (ver comentario do Luan Peres
            # la' pro caso real que motivou essa regra).
            campos = {
                campo_nosso: stats_sofa.get(campo_sofa, 0)
                for campo_sofa, campo_nosso in MAPA_CAMPOS.items()
            }

            db.add(EstatisticaJogadorPartida(
                jogador_id=jogador.id,
                partida_id=partida.id,
                time_id=time_id_nosso,
                gols=stats_sofa.get("goals", 0),
                assistencias=stats_sofa.get("goalAssist", 0),
                cartoes_amarelos=0,
                cartoes_vermelhos=0,
                **campos,
            ))
            criadas += 1
            linhas_existentes.add(jogador.id)

    db.commit()
    return criadas, nao_casados


def backfill_liga(campeonato_id, rodada=None):
    config = CONFIG_LIGA.get(campeonato_id)
    if not config:
        print(f"Campeonato {campeonato_id} nao tem CONFIG_LIGA (mapeamento SofaScore) ainda.")
        return

    db = SessionLocal()
    try:
        campeonato = db.query(Campeonato).get(campeonato_id)

        query = db.query(Partida).filter(Partida.campeonato_id == campeonato_id, Partida.status == "finalizada")
        if rodada is not None:
            query = query.filter(Partida.rodada == rodada)
        partidas = query.all()

        rodadas = sorted({p.rodada for p in partidas})
        cache_eventos = {}
        total_criadas = 0
        total_nao_casados = []

        for r in rodadas:
            if r not in cache_eventos:
                cache_eventos[r] = buscar_eventos_rodada(config["tournament_id"], config["season_id"], r)
            eventos_rodada = cache_eventos[r]

            for partida in [p for p in partidas if p.rodada == r]:
                evento = encontrar_evento(partida, eventos_rodada, config["times"])
                if not evento:
                    continue
                criadas, nao_casados = backfill_partida(db, partida, evento)
                if criadas or nao_casados:
                    msg = f"  Partida {partida.id} rodada {r} ({partida.time_mandante.nome} x {partida.time_visitante.nome}): {criadas} linha(s) criada(s)"
                    if nao_casados:
                        msg += f", nao casou: {nao_casados}"
                    print(msg)
                total_criadas += criadas
                total_nao_casados.extend(nao_casados)

        print(f"\n{campeonato.nome}: {total_criadas} linha(s) criada(s) no total, "
              f"{len(total_nao_casados)} jogador(es) confirmados pelo SofaScore mas nao casados com o elenco.")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: py scripts/backfill_jogadores_sumidos.py <campeonato_id> [rodada]")
        sys.exit(1)
    campeonato_id_arg = int(sys.argv[1])
    rodada_arg = int(sys.argv[2]) if len(sys.argv) > 2 else None
    backfill_liga(campeonato_id_arg, rodada_arg)
