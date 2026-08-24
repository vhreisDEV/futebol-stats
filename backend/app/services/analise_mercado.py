MAX_PERNAS_MULTIPLA = 3  # mais que isso a confianca combinada desaba rapido (produto de taxas <1)

# So mercados com pelo menos 80% de acerto viram bilhete -- mais rigoroso
# que o corte generico de 70% do motor de destaques (usado tambem na
# Dica da Rodada), pra so entregar o que ha de mais "certeiro".
LIMIAR_CERTEIRO = 0.8

# A nota nunca passa de 8/10, mesmo quando a taxa real e' 90% ou 100% --
# mostrar "10/10" venderia uma certeza que rodada nenhuma garante. A
# porcentagem real continua visivel no texto abaixo do card.
TETO_CONFIANCA = 0.8


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
    Bilhete simples = a perna "certeira" (>=80%) de maior taxa isolada.
    Bilhete multipla = as ate MAX_PERNAS_MULTIPLA pernas certeiras de
    maior taxa combinadas, com confianca combinada = produto das taxas
    (assume independencia entre os mercados -- aproximacao razoavel, nao
    uma garantia estatistica). So existe multipla com pelo menos 2 pernas.
    """
    certeiras = [p for p in pernas if p["destaque"]["taxa"] >= LIMIAR_CERTEIRO]
    if not certeiras:
        return None, None

    bilhete_simples = {
        "perna": certeiras[0],
        "confianca": round(min(certeiras[0]["destaque"]["taxa"], TETO_CONFIANCA) * 10, 1),
    }

    if len(certeiras) < 2:
        return bilhete_simples, None

    pernas_multipla = certeiras[:MAX_PERNAS_MULTIPLA]
    confianca_combinada = 1.0
    for p in pernas_multipla:
        confianca_combinada *= p["destaque"]["taxa"]

    bilhete_multipla = {
        "pernas": pernas_multipla,
        "confianca_combinada": round(min(confianca_combinada, TETO_CONFIANCA) * 10, 1),
    }

    return bilhete_simples, bilhete_multipla
