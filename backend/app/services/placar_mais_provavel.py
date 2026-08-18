import math

GOLS_MAXIMO_CONSIDERADO = 8  # placares acima disso sao irrelevantes pra probabilidade
TOP_N_PADRAO = 4


def _poisson_pmf(k, lam):
    return (lam ** k) * math.exp(-lam) / math.factorial(k)


def calcular_placares_mais_provaveis(gols_esperados_mandante, gols_esperados_visitante, top_n=TOP_N_PADRAO):
    """
    Encontra os `top_n` placares exatos mais provaveis a partir dos gols
    esperados de cada time, modelando os gols de cada time como uma
    distribuicao de Poisson independente (abordagem padrao em modelos
    simples de futebol).

    Antes, o "placar mais provavel" era so round(gols_esperados) de cada
    time -- e isso da um resultado sistematicamente errado sempre que a
    media tem parte fracionaria >= 0.5: pra uma Poisson de media 1.6, por
    exemplo, o valor mais provavel de fato e 1 gol (P(1)=32%), nao 2
    (P(2)=26%) -- arredondar pra cima ignora que a Poisson e assimetrica
    (tem uma cauda longa pra direita).

    Mostrar so o placar #1 (melhor exemplo: lider x lanterna, xG 1.5x0.65)
    tambem enganava: 1x0 fica em 17.5%, mas 2x0 (13.1%) e 0x0 (11.6%) vem
    logo atras -- a favoritismo do mandante esta la, só que espalhado
    entre varios placares plausiveis, nao concentrado num so. Por isso
    retorna uma lista top_n (nao so o #1): junto, os primeiros lugares
    deixam visivel que o mandante tende a vencer por 1+ gols, mesmo que
    nenhum placar individual passe de ~20%.
    """
    if gols_esperados_mandante is None or gols_esperados_visitante is None:
        return []

    probs = []
    for gm in range(GOLS_MAXIMO_CONSIDERADO + 1):
        p_gm = _poisson_pmf(gm, gols_esperados_mandante)
        for gv in range(GOLS_MAXIMO_CONSIDERADO + 1):
            p = p_gm * _poisson_pmf(gv, gols_esperados_visitante)
            probs.append((p, gm, gv))

    probs.sort(key=lambda item: item[0], reverse=True)

    return [
        {"gols_mandante": gm, "gols_visitante": gv, "probabilidade": round(p, 4)}
        for p, gm, gv in probs[:top_n]
    ]
