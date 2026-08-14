from app.services.medias import _buscar_jogos_anteriores, _extrair_perspectiva

JANELA_PADRAO = 10
SUAVIZACAO_K = 1  # técnica de Laplace: evita que qualquer resultado fique em 0% ou 100% absoluto


def calcular_forma(db, time_id, data_referencia, janela, mando=None):
    """
    Calcula a forma (contagem e taxas de vitória/empate/derrota) de um time
    nos últimos `janela` jogos anteriores a `data_referencia`, opcionalmente
    filtrando por mando de campo.

    As taxas (taxa_vitoria/taxa_empate/taxa_derrota) usam suavização de
    Laplace: mesmo que um time tenha 0 vitórias na amostra, a taxa não sai
    como exatamente 0% — reflete que a amostra é pequena, não uma
    impossibilidade estatística.
    """
    jogos = _buscar_jogos_anteriores(db, time_id, data_referencia, janela, mando)
    n = len(jogos)

    if n == 0:
        return {
            "jogos_considerados": 0,
            "vitorias": 0,
            "empates": 0,
            "derrotas": 0,
            "taxa_vitoria": None,
            "taxa_empate": None,
            "taxa_derrota": None,
        }

    vitorias = empates = derrotas = 0
    for jogo in jogos:
        p = _extrair_perspectiva(jogo, time_id)
        if p["gols_marcados"] > p["gols_sofridos"]:
            vitorias += 1
        elif p["gols_marcados"] == p["gols_sofridos"]:
            empates += 1
        else:
            derrotas += 1

    denominador_suavizado = n + (3 * SUAVIZACAO_K)

    return {
        "jogos_considerados": n,
        "vitorias": vitorias,
        "empates": empates,
        "derrotas": derrotas,
        "taxa_vitoria": round((vitorias + SUAVIZACAO_K) / denominador_suavizado, 4),
        "taxa_empate": round((empates + SUAVIZACAO_K) / denominador_suavizado, 4),
        "taxa_derrota": round((derrotas + SUAVIZACAO_K) / denominador_suavizado, 4),
    }


def _forma_com_fallback(db, time_id, data_referencia, mando):
    forma = calcular_forma(db, time_id, data_referencia, janela=JANELA_PADRAO, mando=mando)

    if forma["jogos_considerados"] == 0:
        forma = calcular_forma(db, time_id, data_referencia, janela=JANELA_PADRAO, mando=None)
        forma["fallback_para_geral"] = True
    else:
        forma["fallback_para_geral"] = False

    return forma


def calcular_probabilidade_resultado(db, time_mandante_id, time_visitante_id, data_referencia):
    """
    Calcula a probabilidade de vitória do mandante, empate e vitória do
    visitante, com base na frequência histórica (já suavizada) de cada time
    condicionada ao mando de campo.

    As três probabilidades são normalizadas para somar 100%.
    """
    forma_mandante = _forma_com_fallback(db, time_mandante_id, data_referencia, mando="mandante")
    forma_visitante = _forma_com_fallback(db, time_visitante_id, data_referencia, mando="visitante")

    if forma_mandante["jogos_considerados"] == 0 or forma_visitante["jogos_considerados"] == 0:
        return {
            "probabilidade_vitoria_mandante": None,
            "probabilidade_empate": None,
            "probabilidade_vitoria_visitante": None,
            "motivo": "Histórico insuficiente para um dos times, mesmo com fallback para forma geral.",
            "detalhe_mandante": forma_mandante,
            "detalhe_visitante": forma_visitante,
        }

    p_vitoria_mandante_bruta = forma_mandante["taxa_vitoria"]
    p_vitoria_visitante_bruta = forma_visitante["taxa_vitoria"]
    p_empate_bruta = (forma_mandante["taxa_empate"] + forma_visitante["taxa_empate"]) / 2

    soma = p_vitoria_mandante_bruta + p_vitoria_visitante_bruta + p_empate_bruta

    p_vitoria_mandante = round((p_vitoria_mandante_bruta / soma) * 100, 2)
    p_empate = round((p_empate_bruta / soma) * 100, 2)
    p_vitoria_visitante = round((p_vitoria_visitante_bruta / soma) * 100, 2)

    return {
        "probabilidade_vitoria_mandante": p_vitoria_mandante,
        "probabilidade_empate": p_empate,
        "probabilidade_vitoria_visitante": p_vitoria_visitante,
        "janela_usada": JANELA_PADRAO,
        "detalhe_mandante": forma_mandante,
        "detalhe_visitante": forma_visitante,
    }
