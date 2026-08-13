from app.services.medias import calcular_medias

JANELA_PADRAO = 10
LINHA_REFERENCIA_PADRAO = 9.5


def _medias_com_fallback(db, time_id, data_referencia, mando):
    medias = calcular_medias(db, time_id, data_referencia, janela=JANELA_PADRAO, mando=mando)

    if medias["jogos_considerados"] == 0:
        medias = calcular_medias(db, time_id, data_referencia, janela=JANELA_PADRAO, mando=None)
        medias["fallback_para_geral"] = True
    else:
        medias["fallback_para_geral"] = False

    return medias


def calcular_escanteios_esperados(db, time_mandante_id, time_visitante_id, data_referencia,
                                   linha_referencia=LINHA_REFERENCIA_PADRAO):
    """
    Calcula os escanteios esperados de mandante e visitante para uma partida,
    combinando escanteios a favor de um time com escanteios contra do outro.
    Mesma lógica e mesmo fallback da Issue 7 (gols esperados).

    Também calcula uma tendência over/under em relação a uma linha de
    referência (padrão: 9.5 escanteios no total da partida).
    """
    medias_mandante = _medias_com_fallback(db, time_mandante_id, data_referencia, mando="mandante")
    medias_visitante = _medias_com_fallback(db, time_visitante_id, data_referencia, mando="visitante")

    if medias_mandante["jogos_considerados"] == 0 or medias_visitante["jogos_considerados"] == 0:
        return {
            "escanteios_esperados_mandante": None,
            "escanteios_esperados_visitante": None,
            "total_esperado": None,
            "tendencia": None,
            "motivo": "Histórico insuficiente para um dos times, mesmo com fallback para média geral.",
            "detalhe_mandante": medias_mandante,
            "detalhe_visitante": medias_visitante,
        }

    escanteios_esperados_mandante = round(
        (medias_mandante["media_escanteios_a_favor"] + medias_visitante["media_escanteios_contra"]) / 2, 2
    )
    escanteios_esperados_visitante = round(
        (medias_visitante["media_escanteios_a_favor"] + medias_mandante["media_escanteios_contra"]) / 2, 2
    )

    total_esperado = round(escanteios_esperados_mandante + escanteios_esperados_visitante, 2)
    tendencia = "over" if total_esperado > linha_referencia else "under"

    return {
        "escanteios_esperados_mandante": escanteios_esperados_mandante,
        "escanteios_esperados_visitante": escanteios_esperados_visitante,
        "total_esperado": total_esperado,
        "linha_referencia": linha_referencia,
        "tendencia": tendencia,
        "janela_usada": JANELA_PADRAO,
        "detalhe_mandante": medias_mandante,
        "detalhe_visitante": medias_visitante,
    }