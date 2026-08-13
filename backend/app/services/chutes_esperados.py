from app.services.medias import calcular_medias, _buscar_jogos_anteriores

JANELA_PADRAO = 10


def _medias_com_fallback(db, time_id, data_referencia, mando):
    medias = calcular_medias(db, time_id, data_referencia, janela=JANELA_PADRAO, mando=mando)

    if medias["jogos_considerados"] == 0:
        medias = calcular_medias(db, time_id, data_referencia, janela=JANELA_PADRAO, mando=None)
        medias["fallback_para_geral"] = True
    else:
        medias["fallback_para_geral"] = False

    return medias


def _extrair_chutes_1t(partida, time_id):
    if partida.time_mandante_id == time_id:
        return partida.chutes_1t_mandante
    return partida.chutes_1t_visitante


def _media_chutes_1t(db, time_id, data_referencia, mando):
    """
    Calcula a média de chutes no 1º tempo, ignorando jogos sem esse dado
    (comum em dados reais, onde o campo fica nulo). Reporta quantos jogos
    tinham o dado disponível, separado de quantos jogos foram buscados.
    """
    jogos = _buscar_jogos_anteriores(db, time_id, data_referencia, JANELA_PADRAO, mando)
    valores = [v for v in (_extrair_chutes_1t(j, time_id) for j in jogos) if v is not None]

    if not valores:
        return {
            "jogos_buscados": len(jogos),
            "jogos_com_dado": 0,
            "media_chutes_1t": None,
        }

    return {
        "jogos_buscados": len(jogos),
        "jogos_com_dado": len(valores),
        "media_chutes_1t": round(sum(valores) / len(valores), 2),
    }


def calcular_chutes_esperados(db, time_mandante_id, time_visitante_id, data_referencia):
    """
    Calcula chutes totais esperados, chutes ao gol esperados (fórmula
    ataque x defesa, igual gols/escanteios) e chutes no 1º tempo esperados
    (média própria de cada time, ignorando jogos sem esse dado — comum em
    partidas reais, onde o campo é nulo).
    """
    medias_mandante = _medias_com_fallback(db, time_mandante_id, data_referencia, mando="mandante")
    medias_visitante = _medias_com_fallback(db, time_visitante_id, data_referencia, mando="visitante")

    if medias_mandante["jogos_considerados"] == 0 or medias_visitante["jogos_considerados"] == 0:
        return {
            "chutes_totais_esperados_mandante": None,
            "chutes_totais_esperados_visitante": None,
            "chutes_gol_esperados_mandante": None,
            "chutes_gol_esperados_visitante": None,
            "chutes_1t_esperados_mandante": None,
            "chutes_1t_esperados_visitante": None,
            "motivo": "Histórico insuficiente para um dos times, mesmo com fallback para média geral.",
            "detalhe_mandante": medias_mandante,
            "detalhe_visitante": medias_visitante,
        }

    chutes_totais_mandante = round(
        (medias_mandante["media_chutes_a_favor"] + medias_visitante["media_chutes_contra"]) / 2, 2
    )
    chutes_totais_visitante = round(
        (medias_visitante["media_chutes_a_favor"] + medias_mandante["media_chutes_contra"]) / 2, 2
    )

    chutes_gol_mandante = round(
        (medias_mandante["media_chutes_gol_a_favor"] + medias_visitante["media_chutes_gol_contra"]) / 2, 2
    )
    chutes_gol_visitante = round(
        (medias_visitante["media_chutes_gol_a_favor"] + medias_mandante["media_chutes_gol_contra"]) / 2, 2
    )

    chutes_1t_mandante_info = _media_chutes_1t(db, time_mandante_id, data_referencia, mando="mandante")
    chutes_1t_visitante_info = _media_chutes_1t(db, time_visitante_id, data_referencia, mando="visitante")

    chutes_1t_mandante = chutes_1t_mandante_info["media_chutes_1t"]
    chutes_1t_visitante = chutes_1t_visitante_info["media_chutes_1t"]

    return {
        "chutes_totais_esperados_mandante": chutes_totais_mandante,
        "chutes_totais_esperados_visitante": chutes_totais_visitante,
        "chutes_gol_esperados_mandante": chutes_gol_mandante,
        "chutes_gol_esperados_visitante": chutes_gol_visitante,
        "chutes_1t_esperados_mandante": chutes_1t_mandante,
        "chutes_1t_esperados_visitante": chutes_1t_visitante,
        "chutes_1t_detalhe_mandante": chutes_1t_mandante_info,
        "chutes_1t_detalhe_visitante": chutes_1t_visitante_info,
        "janela_usada": JANELA_PADRAO,
        "detalhe_mandante": medias_mandante,
        "detalhe_visitante": medias_visitante,
    }
