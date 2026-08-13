from app.services.medias import calcular_medias

JANELA_PADRAO = 10


def _medias_com_fallback(db, time_id, data_referencia, mando):
    medias = calcular_medias(db, time_id, data_referencia, janela=JANELA_PADRAO, mando=mando)

    if medias["jogos_considerados"] == 0:
        medias = calcular_medias(db, time_id, data_referencia, janela=JANELA_PADRAO, mando=None)
        medias["fallback_para_geral"] = True
    else:
        medias["fallback_para_geral"] = False

    return medias


def calcular_cartoes_esperados(db, time_mandante_id, time_visitante_id, data_referencia):
    """
    Calcula os cartões esperados (amarelos e vermelhos) de mandante e
    visitante para uma partida, com base na própria média de cartões de
    cada time (não combina com o adversário, diferente de gols/escanteios,
    já que cartão depende mais do estilo do time do que do rival).

    Mesmo fallback das Issues 7 e 9: se um time não tiver jogos suficientes
    no recorte de mando, cai para a média geral daquele time.
    """
    medias_mandante = _medias_com_fallback(db, time_mandante_id, data_referencia, mando="mandante")
    medias_visitante = _medias_com_fallback(db, time_visitante_id, data_referencia, mando="visitante")

    if medias_mandante["jogos_considerados"] == 0 or medias_visitante["jogos_considerados"] == 0:
        return {
            "cartoes_amarelos_esperados_mandante": None,
            "cartoes_amarelos_esperados_visitante": None,
            "cartoes_vermelhos_esperados_mandante": None,
            "cartoes_vermelhos_esperados_visitante": None,
            "total_cartoes_esperado": None,
            "motivo": "Histórico insuficiente para um dos times, mesmo com fallback para média geral.",
            "detalhe_mandante": medias_mandante,
            "detalhe_visitante": medias_visitante,
        }

    cartoes_amarelos_mandante = medias_mandante["media_cartoes_amarelos"]
    cartoes_amarelos_visitante = medias_visitante["media_cartoes_amarelos"]
    cartoes_vermelhos_mandante = medias_mandante["media_cartoes_vermelhos"]
    cartoes_vermelhos_visitante = medias_visitante["media_cartoes_vermelhos"]

    total_cartoes_esperado = round(
        cartoes_amarelos_mandante + cartoes_amarelos_visitante
        + cartoes_vermelhos_mandante + cartoes_vermelhos_visitante,
        2,
    )

    return {
        "cartoes_amarelos_esperados_mandante": cartoes_amarelos_mandante,
        "cartoes_amarelos_esperados_visitante": cartoes_amarelos_visitante,
        "cartoes_vermelhos_esperados_mandante": cartoes_vermelhos_mandante,
        "cartoes_vermelhos_esperados_visitante": cartoes_vermelhos_visitante,
        "total_cartoes_esperado": total_cartoes_esperado,
        "janela_usada": JANELA_PADRAO,
        "detalhe_mandante": medias_mandante,
        "detalhe_visitante": medias_visitante,
    }
