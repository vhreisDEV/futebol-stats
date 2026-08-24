MAX_PERNAS_MULTIPLA = 3  # mais que isso a confianca combinada desaba rapido (produto de taxas <1)


def montar_pernas(nome_mandante, destaques_mandante, nome_visitante, destaques_visitante):
    """
    Junta os destaques dos dois times num unico ranking (por taxa de
    acerto), cada um marcado com de quem e' ("mandante em casa" ou
    "visitante fora") -- essa lista ordenada e' a materia-prima tanto do
    bilhete simples quanto da multipla.
    """
    pernas = [{"time": "mandante", "nome_time": nome_mandante, "destaque": d} for d in destaques_mandante]
    pernas += [{"time": "visitante", "nome_time": nome_visitante, "destaque": d} for d in destaques_visitante]
    pernas.sort(key=lambda p: p["destaque"]["taxa"], reverse=True)
    return pernas


def montar_bilhetes(pernas):
    """
    Bilhete simples = a perna de maior taxa isolada (o "melhor mercado").
    Bilhete multipla = as ate MAX_PERNAS_MULTIPLA pernas de maior taxa
    combinadas, com confianca combinada = produto das taxas (assume
    independencia entre os mercados -- aproximacao razoavel, nao uma
    garantia estatistica). So existe multipla com pelo menos 2 pernas.

    Confianca de cada bilhete e' a propria taxa (ou produto de taxas) numa
    escala 0-10, ja que taxa e' naturalmente 0-1.
    """
    if not pernas:
        return None, None

    bilhete_simples = {
        "perna": pernas[0],
        "confianca": round(pernas[0]["destaque"]["taxa"] * 10, 1),
    }

    if len(pernas) < 2:
        return bilhete_simples, None

    pernas_multipla = pernas[:MAX_PERNAS_MULTIPLA]
    confianca_combinada = 1.0
    for p in pernas_multipla:
        confianca_combinada *= p["destaque"]["taxa"]

    bilhete_multipla = {
        "pernas": pernas_multipla,
        "confianca_combinada": round(confianca_combinada * 10, 1),
    }

    return bilhete_simples, bilhete_multipla
