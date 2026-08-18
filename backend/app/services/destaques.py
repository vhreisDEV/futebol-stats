from app.services.medias import _buscar_jogos_anteriores, _extrair_perspectiva

JANELA_PADRAO = 10
MINIMO_JOGOS = 5  # amostra menor que isso nao da pra chamar de "destaque"
TAXA_MINIMA_DESTAQUE = 0.7  # precisa bater em pelo menos 70% dos jogos

# (campo em _extrair_perspectiva, rotulo pra exibir, linhas candidatas --
# os mesmos valores ".5" que uma casa de aposta ofereceria de verdade).
STATS_DESTAQUE = [
    ("escanteios_a_favor", "Escanteios", [2.5, 3.5, 4.5, 5.5, 6.5, 7.5]),
    ("chutes_a_favor", "Chutes", [7.5, 9.5, 11.5, 13.5, 15.5]),
    ("chutes_gol_a_favor", "Chutes ao gol", [1.5, 2.5, 3.5, 4.5, 5.5]),
    ("cartoes_amarelos", "Cartões amarelos", [0.5, 1.5, 2.5, 3.5]),
]


def calcular_destaques_time(db, time_id, mando, data_referencia, janela=JANELA_PADRAO):
    """
    Acha padroes que se repetem nos ultimos jogos de um time, com mando de
    campo fixo (mesmo mando que ele vai ter no proximo jogo -- mandante
    olha so jogos em casa, visitante so jogos fora).

    Pra cada stat, testa um punhado de linhas ".5" (as mesmas que uma casa
    de aposta ofereceria) e fica com a MAIS ALTA que ainda bate em pelo
    menos 70% dos ultimos jogos -- uma linha alta que segue batendo e mais
    notavel que uma linha baixa obvia. Testar contra linhas fixas e
    conhecidas (nao um valor derivado da propria media do time) evita
    inflar a taxa de acerto so por garimpar entre infinitas opcoes: aqui
    sao no maximo 4-6 linhas reais por stat.

    So retorna o que realmente se destaca (>=70% de acerto, >=5 jogos na
    amostra -- "bateu em 3 de 4" nao significa muita coisa). Cada destaque
    inclui a sequencia de valores brutos (mais recente primeiro) pra dar
    transparencia -- o usuario ve os numeros reais por tras da taxa.
    """
    jogos = _buscar_jogos_anteriores(db, time_id, data_referencia, janela, mando)
    if len(jogos) < MINIMO_JOGOS:
        return []

    perspectivas = [_extrair_perspectiva(p, time_id) for p in jogos]

    destaques = []
    for campo, label, linhas_candidatas in STATS_DESTAQUE:
        valores = [p[campo] for p in perspectivas if p[campo] is not None]
        if len(valores) < MINIMO_JOGOS:
            continue

        melhor = None
        for linha in linhas_candidatas:
            acertos = sum(1 for v in valores if v > linha)
            taxa = acertos / len(valores)
            if taxa >= TAXA_MINIMA_DESTAQUE and (melhor is None or linha > melhor["linha"]):
                melhor = {
                    "stat": campo,
                    "label": label,
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
