def escolher_melhor_mercado(nome_mandante, destaques_mandante, nome_visitante, destaques_visitante):
    """
    Entre todos os mercados que se destacaram pros dois times (ja filtrados
    por calcular_destaques_time, >=70% de acerto), fica com o de maior taxa
    -- e' o pitch mais direto pro cliente: "esse e' o mercado mais solido
    pra esse confronto".
    """
    candidatos = [{"time": "mandante", "nome_time": nome_mandante, "destaque": d} for d in destaques_mandante]
    candidatos += [{"time": "visitante", "nome_time": nome_visitante, "destaque": d} for d in destaques_visitante]

    if not candidatos:
        return None

    return max(candidatos, key=lambda c: c["destaque"]["taxa"])
