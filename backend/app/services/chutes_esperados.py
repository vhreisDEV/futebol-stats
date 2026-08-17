from app.services.medias import calcular_medias, _buscar_jogos_anteriores

JANELA_PADRAO = 10
LINHA_REFERENCIA_CHUTES_PADRAO = 24.5  # linha de referencia para total de chutes na partida
LINHA_REFERENCIA_CHUTES_GOL_PADRAO = 8.5  # linha de referencia para total de chutes ao gol na partida


def _medias_com_fallback(db, time_id, data_referencia, mando):
    medias = calcular_medias(db, time_id, data_referencia, janela=JANELA_PADRAO, mando=mando)

    if medias["jogos_considerados"] == 0:
        medias = calcular_medias(db, time_id, data_referencia, janela=JANELA_PADRAO, mando=None)
        medias["fallback_para_geral"] = True
    else:
        medias["fallback_para_geral"] = False

    return medias


def _media_combinada(media_a_favor, media_contra):
    if media_a_favor is None or media_contra is None:
        return None
    return round((media_a_favor + media_contra) / 2, 2)


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


def calcular_chutes_esperados(db, time_mandante_id, time_visitante_id, data_referencia,
                               linha_referencia_geral=LINHA_REFERENCIA_CHUTES_PADRAO,
                               linha_referencia_ao_gol=LINHA_REFERENCIA_CHUTES_GOL_PADRAO):
    """
    Calcula chutes totais esperados, chutes ao gol esperados (fórmula
    ataque x defesa, igual gols/escanteios) e chutes no 1º tempo esperados
    (média própria de cada time, ignorando jogos sem esse dado — comum em
    partidas reais, onde o campo é nulo).

    Também calcula tendência over/under para o total de chutes e para o
    total de chutes ao gol, mesmo padrão usado em escanteios/cartões.
    """
    medias_mandante = _medias_com_fallback(db, time_mandante_id, data_referencia, mando="mandante")
    medias_visitante = _medias_com_fallback(db, time_visitante_id, data_referencia, mando="visitante")

    if medias_mandante["jogos_considerados"] == 0 or medias_visitante["jogos_considerados"] == 0:
        return {
            "chutes_totais_esperados_mandante": None,
            "chutes_totais_esperados_visitante": None,
            "total_geral_esperado": None,
            "linha_referencia_geral": linha_referencia_geral,
            "tendencia_geral": None,
            "chutes_gol_esperados_mandante": None,
            "chutes_gol_esperados_visitante": None,
            "total_ao_gol_esperado": None,
            "linha_referencia_ao_gol": linha_referencia_ao_gol,
            "tendencia_ao_gol": None,
            "chutes_1t_esperados_mandante": None,
            "chutes_1t_esperados_visitante": None,
            "motivo": "Histórico insuficiente para um dos times, mesmo com fallback para média geral.",
            "detalhe_mandante": medias_mandante,
            "detalhe_visitante": medias_visitante,
        }

    # Times com jogos no historico mas sem chutes/chutes ao gol registrados
    # ainda (ex.: placar que veio so do PDF da CBF, sem estatisticas
    # granulares) tem media_* = None -- calcula so o que da pra calcular,
    # em vez de quebrar tentando somar com None.
    chutes_totais_mandante = _media_combinada(
        medias_mandante["media_chutes_a_favor"], medias_visitante["media_chutes_contra"]
    )
    chutes_totais_visitante = _media_combinada(
        medias_visitante["media_chutes_a_favor"], medias_mandante["media_chutes_contra"]
    )

    chutes_gol_mandante = _media_combinada(
        medias_mandante["media_chutes_gol_a_favor"], medias_visitante["media_chutes_gol_contra"]
    )
    chutes_gol_visitante = _media_combinada(
        medias_visitante["media_chutes_gol_a_favor"], medias_mandante["media_chutes_gol_contra"]
    )

    if chutes_totais_mandante is not None and chutes_totais_visitante is not None:
        total_geral_esperado = round(chutes_totais_mandante + chutes_totais_visitante, 2)
        tendencia_geral = "over" if total_geral_esperado > linha_referencia_geral else "under"
    else:
        total_geral_esperado = None
        tendencia_geral = None

    if chutes_gol_mandante is not None and chutes_gol_visitante is not None:
        total_ao_gol_esperado = round(chutes_gol_mandante + chutes_gol_visitante, 2)
        tendencia_ao_gol = "over" if total_ao_gol_esperado > linha_referencia_ao_gol else "under"
    else:
        total_ao_gol_esperado = None
        tendencia_ao_gol = None

    chutes_1t_mandante_info = _media_chutes_1t(db, time_mandante_id, data_referencia, mando="mandante")
    chutes_1t_visitante_info = _media_chutes_1t(db, time_visitante_id, data_referencia, mando="visitante")

    chutes_1t_mandante = chutes_1t_mandante_info["media_chutes_1t"]
    chutes_1t_visitante = chutes_1t_visitante_info["media_chutes_1t"]

    return {
        "chutes_totais_esperados_mandante": chutes_totais_mandante,
        "chutes_totais_esperados_visitante": chutes_totais_visitante,
        "total_geral_esperado": total_geral_esperado,
        "linha_referencia_geral": linha_referencia_geral,
        "tendencia_geral": tendencia_geral,
        "chutes_gol_esperados_mandante": chutes_gol_mandante,
        "chutes_gol_esperados_visitante": chutes_gol_visitante,
        "total_ao_gol_esperado": total_ao_gol_esperado,
        "linha_referencia_ao_gol": linha_referencia_ao_gol,
        "tendencia_ao_gol": tendencia_ao_gol,
        "chutes_1t_esperados_mandante": chutes_1t_mandante,
        "chutes_1t_esperados_visitante": chutes_1t_visitante,
        "chutes_1t_detalhe_mandante": chutes_1t_mandante_info,
        "chutes_1t_detalhe_visitante": chutes_1t_visitante_info,
        "janela_usada": JANELA_PADRAO,
        "detalhe_mandante": medias_mandante,
        "detalhe_visitante": medias_visitante,
    }
