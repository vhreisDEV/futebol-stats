from sqlalchemy import and_, or_, func
from app.models.partida import Partida


def ultimo_jogo_finalizado(db, time_id):
    """Data do jogo finalizado mais recente de um time (mandante ou
    visitante) -- usado pra saber se o cache de destaques de um time
    ainda vale (ver AnaliseIAPartida.mandante_ultimo_jogo/
    visitante_ultimo_jogo): se essa data nao mudou desde que o cache foi
    calculado, os ultimos jogos considerados sao exatamente os mesmos."""
    return (
        db.query(func.max(Partida.data))
        .filter(Partida.status == "finalizada", or_(Partida.time_mandante_id == time_id, Partida.time_visitante_id == time_id))
        .scalar()
    )


def _buscar_jogos_anteriores(db, time_id, data_referencia, janela, mando=None):
    """
    Busca os últimos `janela` jogos de um time, estritamente anteriores
    a `data_referencia` (nunca inclui o próprio jogo nem jogos futuros).

    mando:
        None       -> jogos como mandante ou visitante (geral)
        "mandante" -> apenas jogos em casa
        "visitante"-> apenas jogos fora
    """
    query = db.query(Partida).filter(Partida.data < data_referencia, Partida.status == "finalizada")

    if mando == "mandante":
        query = query.filter(Partida.time_mandante_id == time_id)
    elif mando == "visitante":
        query = query.filter(Partida.time_visitante_id == time_id)
    else:
        query = query.filter(
            or_(Partida.time_mandante_id == time_id, Partida.time_visitante_id == time_id)
        )

    return (
        query.order_by(Partida.data.desc())
        .limit(janela)
        .all()
    )


def _extrair_perspectiva(partida, time_id):
    """
    Reorganiza os campos de uma partida do ponto de vista de `time_id`,
    devolvendo (gols_marcados, gols_sofridos, escanteios_a_favor,
    escanteios_contra, chutes_a_favor, chutes_contra, chutes_gol_a_favor,
    chutes_gol_contra, cartoes_amarelos, cartoes_vermelhos).
    """
    if partida.time_mandante_id == time_id:
        return {
            "gols_marcados": partida.gols_mandante,
            "gols_sofridos": partida.gols_visitante,
            "escanteios_a_favor": partida.escanteios_mandante,
            "escanteios_contra": partida.escanteios_visitante,
            "chutes_a_favor": partida.chutes_mandante,
            "chutes_contra": partida.chutes_visitante,
            "chutes_gol_a_favor": partida.chutes_gol_mandante,
            "chutes_gol_contra": partida.chutes_gol_visitante,
            "cartoes_amarelos": partida.cartoes_amarelos_mandante,
            "cartoes_vermelhos": partida.cartoes_vermelhos_mandante,
        }
    else:
        return {
            "gols_marcados": partida.gols_visitante,
            "gols_sofridos": partida.gols_mandante,
            "escanteios_a_favor": partida.escanteios_visitante,
            "escanteios_contra": partida.escanteios_mandante,
            "chutes_a_favor": partida.chutes_visitante,
            "chutes_contra": partida.chutes_mandante,
            "chutes_gol_a_favor": partida.chutes_gol_visitante,
            "chutes_gol_contra": partida.chutes_gol_mandante,
            "cartoes_amarelos": partida.cartoes_amarelos_visitante,
            "cartoes_vermelhos": partida.cartoes_vermelhos_visitante,
        }


def calcular_medias(db, time_id, data_referencia, janela=5, mando=None):
    """
    Calcula as médias estatísticas de um time nos últimos `janela` jogos
    anteriores a `data_referencia`, opcionalmente filtrando por mando de campo.

    Retorna um dicionário com as médias e o número de jogos efetivamente
    encontrados (pode ser menor que `janela` se o time não tiver histórico
    suficiente).
    """
    jogos = _buscar_jogos_anteriores(db, time_id, data_referencia, janela, mando)
    n = len(jogos)

    if n == 0:
        return {
            "jogos_considerados": 0,
            "media_gols_marcados": None,
            "media_gols_sofridos": None,
            "media_escanteios_a_favor": None,
            "media_escanteios_contra": None,
            "media_chutes_a_favor": None,
            "media_chutes_contra": None,
            "media_chutes_gol_a_favor": None,
            "media_chutes_gol_contra": None,
            "media_cartoes_amarelos": None,
            "media_cartoes_vermelhos": None,
        }

    perspectivas = [_extrair_perspectiva(p, time_id) for p in jogos]

    def media(campo):
        # Alguns jogos podem ter placar (gols) sem as estatisticas mais
        # granulares ainda (ex.: placar que veio so do PDF da CBF). Tira a
        # media so dos jogos que realmente tem o campo, em vez de quebrar
        # ou fingir que o valor ausente e zero.
        valores = [p[campo] for p in perspectivas if p[campo] is not None]
        if not valores:
            return None
        return round(sum(valores) / len(valores), 2)

    return {
        "jogos_considerados": n,
        "media_gols_marcados": media("gols_marcados"),
        "media_gols_sofridos": media("gols_sofridos"),
        "media_escanteios_a_favor": media("escanteios_a_favor"),
        "media_escanteios_contra": media("escanteios_contra"),
        "media_chutes_a_favor": media("chutes_a_favor"),
        "media_chutes_contra": media("chutes_contra"),
        "media_chutes_gol_a_favor": media("chutes_gol_a_favor"),
        "media_chutes_gol_contra": media("chutes_gol_contra"),
        "media_cartoes_amarelos": media("cartoes_amarelos"),
        "media_cartoes_vermelhos": media("cartoes_vermelhos"),
    }


def calcular_medias_completas(db, time_id, data_referencia):
    """
    Calcula todas as combinações de janela (5 e 10) e mando (geral,
    mandante, visitante) para um time, de uma vez.
    """
    resultado = {}
    for janela in (5, 10):
        for mando, chave in ((None, "geral"), ("mandante", "mandante"), ("visitante", "visitante")):
            resultado[f"janela_{janela}_{chave}"] = calcular_medias(
                db, time_id, data_referencia, janela=janela, mando=mando
            )
    return resultado
