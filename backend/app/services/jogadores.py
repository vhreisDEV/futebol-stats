from sqlalchemy import func
from app.models.jogador import Jogador
from app.models.estatistica_jogador_partida import EstatisticaJogadorPartida
from app.models.partida import Partida
from app.models.time import Time

# Estatisticas que o usuario quer acompanhar: chutes, chutes ao gol,
# faltas cometidas/sofridas, desarmes, gol/assistencia, cartoes.
STATS_VALIDAS = {
    "gols": EstatisticaJogadorPartida.gols,
    "assistencias": EstatisticaJogadorPartida.assistencias,
    "chutes": EstatisticaJogadorPartida.chutes,
    "chutes_gol": EstatisticaJogadorPartida.chutes_gol,
    "desarmes": EstatisticaJogadorPartida.desarmes,
    "faltas_cometidas": EstatisticaJogadorPartida.faltas_cometidas,
    "faltas_sofridas": EstatisticaJogadorPartida.faltas_sofridas,
    "cartoes_amarelos": EstatisticaJogadorPartida.cartoes_amarelos,
    "cartoes_vermelhos": EstatisticaJogadorPartida.cartoes_vermelhos,
}


def calcular_ranking(db, stat, limit=20):
    coluna = STATS_VALIDAS.get(stat)
    if coluna is None:
        return None

    linhas = (
        db.query(
            Jogador.id.label("jogador_id"),
            Jogador.nome,
            Jogador.posicao,
            Time.id.label("time_id"),
            Time.nome.label("time_nome"),
            func.count(EstatisticaJogadorPartida.id).label("jogos"),
            func.sum(coluna).label("total"),
        )
        .join(EstatisticaJogadorPartida, EstatisticaJogadorPartida.jogador_id == Jogador.id)
        .outerjoin(Time, Time.id == Jogador.time_id)
        .filter(coluna.isnot(None))
        .group_by(Jogador.id)
        .order_by(func.sum(coluna).desc())
        .limit(limit)
        .all()
    )

    resultado = []
    for linha in linhas:
        total = linha.total or 0
        resultado.append(
            {
                "jogador_id": linha.jogador_id,
                "nome": linha.nome,
                "posicao": linha.posicao,
                "time_id": linha.time_id,
                "time_nome": linha.time_nome,
                "jogos": linha.jogos,
                "total": total,
                "media": round(total / linha.jogos, 2) if linha.jogos else 0,
            }
        )
    return resultado


def obter_ultimos_jogos_jogador(db, jogador_id, quantidade=10):
    linhas = (
        db.query(EstatisticaJogadorPartida)
        .join(Partida, Partida.id == EstatisticaJogadorPartida.partida_id)
        .filter(EstatisticaJogadorPartida.jogador_id == jogador_id)
        .order_by(Partida.data.desc())
        .limit(quantidade)
        .all()
    )

    return [_montar_jogo_jogador(linha) for linha in linhas]


def _montar_jogo_jogador(linha):
    partida = linha.partida
    jogou_em_casa = partida.time_mandante_id == linha.time_id
    adversario = partida.time_visitante.nome if jogou_em_casa else partida.time_mandante.nome

    return {
        "id": linha.id,
        "partida_id": partida.id,
        "data": partida.data,
        "adversario": adversario,
        "casa_ou_fora": "casa" if jogou_em_casa else "fora",
        "minutos_jogados": linha.minutos_jogados,
        "gols": linha.gols,
        "assistencias": linha.assistencias,
        "chutes": linha.chutes,
        "chutes_gol": linha.chutes_gol,
        "desarmes": linha.desarmes,
        "faltas_cometidas": linha.faltas_cometidas,
        "faltas_sofridas": linha.faltas_sofridas,
        "cartoes_amarelos": linha.cartoes_amarelos,
        "cartoes_vermelhos": linha.cartoes_vermelhos,
    }
