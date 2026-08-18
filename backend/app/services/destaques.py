from app.services.medias import _buscar_jogos_anteriores, _extrair_perspectiva

JANELA_PADRAO = 10
MINIMO_JOGOS = 5  # amostra menor que isso nao da pra chamar de "destaque"
TAXA_MINIMA_DESTAQUE = 0.7  # precisa bater em pelo menos 70% dos jogos


def _serie_campo(campo):
    """Extrai a serie bruta de um campo direto de _extrair_perspectiva."""

    def extrator(perspectivas):
        return [p[campo] for p in perspectivas if p[campo] is not None]

    return extrator


def _serie_ambas_marcam(perspectivas):
    return [
        1 if p["gols_marcados"] > 0 and p["gols_sofridos"] > 0 else 0
        for p in perspectivas
        if p["gols_marcados"] is not None and p["gols_sofridos"] is not None
    ]


def _serie_sem_perder(perspectivas):
    return [
        1 if p["gols_marcados"] >= p["gols_sofridos"] else 0
        for p in perspectivas
        if p["gols_marcados"] is not None and p["gols_sofridos"] is not None
    ]


# "quantidade": linha e um valor real (escanteios, chutes, gols...).
# "booleano": a serie e so 0/1 (aconteceu ou nao no jogo) -- so existe uma
# linha candidata (0.5, i.e. "aconteceu"), o front mostra Sim/Nao em vez
# do numero bruto.
STATS_DESTAQUE = [
    {
        "chave": "gols_marcados",
        "label": "Gols marcados",
        "tipo": "quantidade",
        "linhas": [0.5, 1.5, 2.5, 3.5],
        "extrator": _serie_campo("gols_marcados"),
    },
    {
        "chave": "escanteios_a_favor",
        "label": "Escanteios",
        "tipo": "quantidade",
        "linhas": [2.5, 3.5, 4.5, 5.5, 6.5, 7.5],
        "extrator": _serie_campo("escanteios_a_favor"),
    },
    {
        "chave": "chutes_a_favor",
        "label": "Chutes",
        "tipo": "quantidade",
        "linhas": [7.5, 9.5, 11.5, 13.5, 15.5],
        "extrator": _serie_campo("chutes_a_favor"),
    },
    {
        "chave": "chutes_gol_a_favor",
        "label": "Chutes ao gol",
        "tipo": "quantidade",
        "linhas": [1.5, 2.5, 3.5, 4.5, 5.5],
        "extrator": _serie_campo("chutes_gol_a_favor"),
    },
    {
        "chave": "cartoes_amarelos",
        "label": "Cartões amarelos",
        "tipo": "quantidade",
        "linhas": [0.5, 1.5, 2.5, 3.5],
        "extrator": _serie_campo("cartoes_amarelos"),
    },
    {
        "chave": "ambas_marcam",
        "label": "Ambas equipes marcam",
        "tipo": "booleano",
        "linhas": [0.5],
        "extrator": _serie_ambas_marcam,
    },
    {
        "chave": "sem_perder",
        "label": "Não perde",
        "tipo": "booleano",
        "linhas": [0.5],
        "extrator": _serie_sem_perder,
    },
]


def calcular_destaques_time(db, time_id, mando, data_referencia, janela=JANELA_PADRAO):
    """
    Acha padroes que se repetem nos ultimos jogos de um time, com mando de
    campo fixo (mesmo mando que ele vai ter no proximo jogo -- mandante
    olha so jogos em casa, visitante so jogos fora).

    Pra stats numericos, testa um punhado de linhas ".5" fixas (as mesmas
    que uma casa de aposta ofereceria) e fica com a MAIS ALTA que ainda
    bate em pelo menos 70% dos ultimos jogos. Testar contra linhas fixas e
    conhecidas (nao um valor derivado da propria media do time) evita
    inflar a taxa de acerto so por garimpar entre infinitas opcoes.

    Pra stats booleanos (ambas marcam, nao perde), a "serie" ja e 0/1 por
    jogo e so existe uma linha candidata (0.5 = aconteceu).

    So retorna o que realmente se destaca (>=70% de acerto, >=5 jogos na
    amostra). Cada destaque inclui a sequencia de valores brutos (mais
    recente primeiro) pra dar transparencia.
    """
    jogos = _buscar_jogos_anteriores(db, time_id, data_referencia, janela, mando)
    if len(jogos) < MINIMO_JOGOS:
        return []

    perspectivas = [_extrair_perspectiva(p, time_id) for p in jogos]

    destaques = []
    for stat in STATS_DESTAQUE:
        valores = stat["extrator"](perspectivas)
        if len(valores) < MINIMO_JOGOS:
            continue

        melhor = None
        for linha in stat["linhas"]:
            acertos = sum(1 for v in valores if v > linha)
            taxa = acertos / len(valores)
            if taxa >= TAXA_MINIMA_DESTAQUE and (melhor is None or linha > melhor["linha"]):
                melhor = {
                    "stat": stat["chave"],
                    "label": stat["label"],
                    "tipo": stat["tipo"],
                    "linha": linha,
                    "acertos": acertos,
                    "total": len(valores),
                    "taxa": round(taxa, 4),
                    "sequencia": valores,
                    "media": round(sum(valores) / len(valores), 2),
                }

        if melhor:
            destaques.append(melhor)

    destaques.sort(key=lambda d: d["taxa"], reverse=True)
    return destaques
