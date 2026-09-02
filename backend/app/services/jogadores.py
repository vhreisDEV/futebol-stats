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


def calcular_ranking(db, stat, limit=20, mando=None, time_id=None, campeonato_id=None):
    coluna = STATS_VALIDAS.get(stat)
    if coluna is None:
        return None

    if time_id is not None:
        linhas = _ranking_elenco_completo(db, coluna, mando, time_id, stat)
    else:
        linhas = _ranking_top_liga(db, coluna, mando, limit, stat, campeonato_id)

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


def _ranking_top_liga(db, coluna, mando, limit, stat, campeonato_id=None):
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

    if campeonato_id is not None:
        query = query.filter(Time.campeonato_id == campeonato_id)

    if stat in STATS_SO_GOLEIRO:
        query = query.filter(Jogador.posicao == "Goleiro")

    filtro_mando = _filtro_mando_stat(mando)
    if filtro_mando is not None:
        query = query.join(Partida, Partida.id == EstatisticaJogadorPartida.partida_id).filter(filtro_mando)

    # Postgres exige que toda coluna selecionada esteja no GROUP BY ou seja
    # agregada (SQLite deixa passar por ser tolerante demais) -- Time.id
    # precisa entrar aqui porque Time.nome vem de outra tabela via join.
    return query.group_by(Jogador.id, Time.id).order_by(func.sum(coluna).desc()).limit(limit).all()


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
        query.group_by(Jogador.id, Time.id)
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


def obter_grade_time(db, time_id, stat, quantidade=10, mando=None):
    """Grade estilo PlayerStats.com: colunas = ultimos N jogos do time,
    linhas = jogadores que jogaram pelo menos um desses jogos por ESSE
    time. Um jogador que nao jogou um jogo especifico (poupado,
    lesionado, ainda nao tinha chegado no elenco) fica com valor None
    naquela coluna -- diferente de 0, que seria "jogou e nao fez nada".

    Busca os candidatos pelas proprias linhas de EstatisticaJogadorPartida
    do time NESSES jogos (nao por Jogador.time_id, que reflete o time
    ATUAL do jogador e quebraria pra quem foi transferido depois --
    mesma licao do bug real encontrado no enriquecimento via SofaScore,
    ver enriquecer_sofascore.py)."""
    coluna = STATS_VALIDAS.get(stat)
    if coluna is None:
        return None

    query = (
        db.query(Partida)
        .filter(
            Partida.status == "finalizada",
            (Partida.time_mandante_id == time_id) | (Partida.time_visitante_id == time_id),
        )
    )
    if mando == "casa":
        query = query.filter(Partida.time_mandante_id == time_id)
    elif mando == "fora":
        query = query.filter(Partida.time_visitante_id == time_id)

    partidas = query.order_by(Partida.data.desc()).limit(quantidade).all()
    if not partidas:
        return {"stat": stat, "jogos": [], "jogadores": []}

    partida_por_id = {p.id: p for p in partidas}
    linhas = (
        db.query(EstatisticaJogadorPartida)
        .filter(
            EstatisticaJogadorPartida.partida_id.in_(partida_por_id.keys()),
            EstatisticaJogadorPartida.time_id == time_id,
        )
        .all()
    )

    jogadores_por_id = {}
    valores_por_jogador = {}
    for linha in linhas:
        valores_por_jogador.setdefault(linha.jogador_id, {})[linha.partida_id] = getattr(linha, stat)
        if linha.jogador_id not in jogadores_por_id:
            jogadores_por_id[linha.jogador_id] = linha.jogador

    if stat in STATS_SO_GOLEIRO:
        jogadores_por_id = {
            jid: j for jid, j in jogadores_por_id.items() if j.posicao == "Goleiro"
        }

    jogos_resposta = [_montar_jogo_time(p, time_id) for p in partidas]

    jogadores_resposta = []
    for jogador_id, jogador in jogadores_por_id.items():
        valores_partida = valores_por_jogador[jogador_id]
        valores = [valores_partida.get(p.id) for p in partidas]
        valores_validos = [v for v in valores if v is not None]
        total = sum(valores_validos)
        jogadores_resposta.append(
            {
                "jogador_id": jogador_id,
                "nome": jogador.nome,
                "posicao": jogador.posicao,
                "total": total,
                "media": round(total / len(valores_validos), 2) if valores_validos else 0,
                "valores": valores,
            }
        )

    jogadores_resposta.sort(key=lambda j: j["total"], reverse=True)

    return {"stat": stat, "jogos": jogos_resposta, "jogadores": jogadores_resposta}


def _montar_jogo_time(partida, time_id):
    jogou_em_casa = partida.time_mandante_id == time_id
    adversario = partida.time_visitante.nome if jogou_em_casa else partida.time_mandante.nome
    gols_time = partida.gols_mandante if jogou_em_casa else partida.gols_visitante
    gols_adversario = partida.gols_visitante if jogou_em_casa else partida.gols_mandante
    return {
        "partida_id": partida.id,
        "data": partida.data,
        "adversario": adversario,
        "casa_ou_fora": "casa" if jogou_em_casa else "fora",
        "placar": f"{gols_time}-{gols_adversario}" if gols_time is not None else None,
    }


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
