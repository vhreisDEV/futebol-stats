from app.services.medias import calcular_medias

JANELA_PADRAO = 10


def _medias_com_fallback(db, time_id, data_referencia, mando):
    """
    Tenta calcular médias filtradas por mando de campo (mandante/visitante).
    Se o time não tiver jogos suficientes nesse recorte (jogos_considerados == 0),
    cai para as médias gerais (sem filtro de mando) como fallback.
    """
    medias = calcular_medias(db, time_id, data_referencia, janela=JANELA_PADRAO, mando=mando)

    if medias["jogos_considerados"] == 0:
        medias = calcular_medias(db, time_id, data_referencia, janela=JANELA_PADRAO, mando=None)
        medias["fallback_para_geral"] = True
    else:
        medias["fallback_para_geral"] = False

    return medias


def calcular_gols_esperados(db, time_mandante_id, time_visitante_id, data_referencia):
    """
    Calcula os gols esperados de mandante e visitante para uma partida,
    combinando o ataque de um time com a defesa do outro.

    gols_esperados_mandante = (média de gols marcados pelo mandante em casa
                                + média de gols sofridos pelo visitante fora) / 2
    gols_esperados_visitante = (média de gols marcados pelo visitante fora
                                 + média de gols sofridos pelo mandante em casa) / 2

    Usa janela de 10 jogos. Se um time não tiver jogos suficientes no recorte
    de mando de campo (ex.: time novo, sem jogos fora ainda), cai para a
    média geral daquele time como fallback.
    """
    medias_mandante = _medias_com_fallback(db, time_mandante_id, data_referencia, mando="mandante")
    medias_visitante = _medias_com_fallback(db, time_visitante_id, data_referencia, mando="visitante")

    if medias_mandante["jogos_considerados"] == 0 or medias_visitante["jogos_considerados"] == 0:
        return {
            "gols_esperados_mandante": None,
            "gols_esperados_visitante": None,
            "motivo": "Histórico insuficiente para um dos times, mesmo com fallback para média geral.",
            "detalhe_mandante": medias_mandante,
            "detalhe_visitante": medias_visitante,
        }

    gols_esperados_mandante = round(
        (medias_mandante["media_gols_marcados"] + medias_visitante["media_gols_sofridos"]) / 2, 2
    )
    gols_esperados_visitante = round(
        (medias_visitante["media_gols_marcados"] + medias_mandante["media_gols_sofridos"]) / 2, 2
    )

    return {
        "gols_esperados_mandante": gols_esperados_mandante,
        "gols_esperados_visitante": gols_esperados_visitante,
        "janela_usada": JANELA_PADRAO,
        "detalhe_mandante": medias_mandante,
        "detalhe_visitante": medias_visitante,
    }
