from sqlalchemy import func, case
from app.models.jogador import Jogador
from app.models.estatistica_jogador_partida import EstatisticaJogadorPartida
from app.models.partida import Partida
from app.models.time import Time

# Estatisticas que o usuario quer acompanhar: chutes, chutes ao gol,
# faltas cometidas/sofridas, desarmes, gol/assistencia, cartoes, defesas.
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
    "defesas": EstatisticaJogadorPartida.defesas,
}

# Estatisticas que so fazem sentido para goleiros.
STATS_SO_GOLEIRO = {"defesas"}


def _filtro_mando_stat(mando):
    if mando == "casa":
        return Partida.time_mandante_id == EstatisticaJogadorPartida.time_id
    if mando == "fora":
        return Partida.time_visitante_id == EstatisticaJogadorPartida.time_id
    return None


def calcular_ranking(db, stat, limit=20, mando=None, time_id=None):
    coluna = STATS_VALIDAS.get(stat)
    if coluna is None:
        return None

    if time_id is not None:
        linhas = _ranking_elenco_completo(db, coluna, mando, time_id, stat)
    else:
        linhas = _ranking_top_liga(db, coluna, mando, limit, stat)

    resultado = []
    for linha in linhas:
        total = linha.total or 0
        jogos = linha.jogos or 0
        resultado.append(
            {
                "jogador_id": linha.jogador_id,
                "nome": linha.nome,
                "posicao": linha.posicao,
                "time_id": linha.time_id,
                "time_nome": linha.time_nome,
                "jogos": jogos,
                "total": total,
                "media": round(total / jogos, 2) if jogos else 0,
            }
        )
    return resultado


def _ranking_top_liga(db, coluna, mando, limit, stat):
    query = (
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
    )

    if stat in STATS_SO_GOLEIRO:
        query = query.filter(Jogador.posicao == "Goleiro")

    filtro_mando = _filtro_mando_stat(mando)
    if filtro_mando is not None:
        query = query.join(Partida, Partida.id == EstatisticaJogadorPartida.partida_id).filter(filtro_mando)

    return query.group_by(Jogador.id).order_by(func.sum(coluna).desc()).limit(limit).all()


def _ranking_elenco_completo(db, coluna, mando, time_id, stat):
    """Todos os jogadores do time, mesmo sem nenhuma estatistica na
    categoria escolhida (aparecem com total 0), para dar pra achar
    qualquer jogador do elenco -- nao so quem entra no top da liga."""
    condicao_mando = _filtro_mando_stat(mando)
    if condicao_mando is not None:
        expressao_total = func.sum(case((condicao_mando, coluna), else_=0))
        expressao_jogos = func.sum(case((condicao_mando, 1), else_=0))
    else:
        expressao_total = func.sum(coluna)
        expressao_jogos = func.count(EstatisticaJogadorPartida.id)

    query = (
        db.query(
            Jogador.id.label("jogador_id"),
            Jogador.nome,
            Jogador.posicao,
            Time.id.label("time_id"),
            Time.nome.label("time_nome"),
            func.coalesce(expressao_jogos, 0).label("jogos"),
            func.coalesce(expressao_total, 0).label("total"),
        )
        .outerjoin(Time, Time.id == Jogador.time_id)
        .outerjoin(EstatisticaJogadorPartida, EstatisticaJogadorPartida.jogador_id == Jogador.id)
        .outerjoin(Partida, Partida.id == EstatisticaJogadorPartida.partida_id)
        .filter(Jogador.time_id == time_id)
    )

    if stat in STATS_SO_GOLEIRO:
        query = query.filter(Jogador.posicao == "Goleiro")

    return (
        query.group_by(Jogador.id)
        .order_by(func.coalesce(expressao_total, 0).desc())
        .all()
    )


def obter_ultimos_jogos_jogador(db, jogador_id, quantidade=10, mando=None):
    query = (
        db.query(EstatisticaJogadorPartida)
        .join(Partida, Partida.id == EstatisticaJogadorPartida.partida_id)
        .filter(EstatisticaJogadorPartida.jogador_id == jogador_id)
    )

    filtro_mando = _filtro_mando_stat(mando)
    if filtro_mando is not None:
        query = query.filter(filtro_mando)

    linhas = query.order_by(Partida.data.desc()).limit(quantidade).all()

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
        "defesas": linha.defesas,
        "cartoes_amarelos": linha.cartoes_amarelos,
        "cartoes_vermelhos": linha.cartoes_vermelhos,
    }
