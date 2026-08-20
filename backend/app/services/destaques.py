from app.models.jogador import Jogador
from app.services.medias import _buscar_jogos_anteriores, _extrair_perspectiva
from app.services.jogadores import obter_ultimos_jogos_jogador

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


def _encontrar_destaques(valores_de_entrada, definicoes_stats):
    """
    Nucleo comum entre destaque de time e de jogador: pra cada stat
    definido, extrai a serie e acha a linha mais alta que ainda bate em
    pelo menos TAXA_MINIMA_DESTAQUE dos jogos (>= MINIMO_JOGOS na
    amostra). Ver docstring de calcular_destaques_time pra por que a
    linha e fixa (nao derivada da propria media).
    """
    destaques = []
    for stat in definicoes_stats:
        valores = stat["extrator"](valores_de_entrada)
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


# "quantidade": linha e um valor real (escanteios, chutes, gols...).
# "booleano": a serie e so 0/1 (aconteceu ou nao no jogo) -- so existe uma
# linha candidata (0.5, i.e. "aconteceu"), o front mostra Sim/Nao em vez
# do numero bruto.
STATS_DESTAQUE_TIME = [
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
    return _encontrar_destaques(perspectivas, STATS_DESTAQUE_TIME)


def _serie_campo_jogo(campo):
    def extrator(jogos):
        return [j[campo] for j in jogos if j[campo] is not None]

    return extrator


# So gols/assistencias/cartoes -- a Highlightly nao da chutes/desarmes/
# faltas por jogador (confirmado 2026-08-19), entao nao tem serie pra
# testar nesses campos.
STATS_DESTAQUE_JOGADOR = [
    {
        "chave": "gols",
        "label": "Gols",
        "tipo": "quantidade",
        "linhas": [0.5, 1.5, 2.5],
        "extrator": _serie_campo_jogo("gols"),
    },
    {
        "chave": "assistencias",
        "label": "Assistências",
        "tipo": "quantidade",
        "linhas": [0.5, 1.5],
        "extrator": _serie_campo_jogo("assistencias"),
    },
    {
        "chave": "cartoes_amarelos",
        "label": "Cartões amarelos",
        "tipo": "quantidade",
        "linhas": [0.5, 1.5],
        "extrator": _serie_campo_jogo("cartoes_amarelos"),
    },
]


def calcular_destaques_jogador(db, jogador_id, janela=JANELA_PADRAO):
    """
    Mesma logica de calcular_destaques_time, mas pra um jogador --
    gols/assistencias/cartoes (o unico dado por jogador que a Highlightly
    da, ver [[project_veaga_player_stats_idea]]).

    Nao separa por mando de campo (diferente do time): com o backfill de
    jogador ainda parcial, dividir por casa/fora corta a amostra praticamente
    pela metade e a maioria dos jogadores nem bate o minimo de 5 jogos
    ainda. Revisitar quando o historico completo estiver importado.
    """
    jogos = obter_ultimos_jogos_jogador(db, jogador_id, quantidade=janela, mando=None)
    if len(jogos) < MINIMO_JOGOS:
        return []

    return _encontrar_destaques(jogos, STATS_DESTAQUE_JOGADOR)


def calcular_destaques_jogadores_time(db, time_id, janela=JANELA_PADRAO, limite=3):
    """Pra cada jogador do elenco atual do time, roda calcular_destaques_jogador
    e so devolve quem realmente tem algum destaque (evita listar o elenco
    inteiro so pra maioria vir vazia). Corta pros `limite` jogadores com a
    maior taxa de acerto, pra nao afogar o card do confronto com o elenco
    inteiro."""
    jogadores = db.query(Jogador).filter(Jogador.time_id == time_id).all()

    resultado = []
    for jogador in jogadores:
        destaques = calcular_destaques_jogador(db, jogador.id, janela)
        if destaques:
            resultado.append(
                {
                    "jogador_id": jogador.id,
                    "nome": jogador.nome,
                    "posicao": jogador.posicao,
                    "destaques": destaques,
                }
            )

    resultado.sort(key=lambda j: max(d["taxa"] for d in j["destaques"]), reverse=True)
    return resultado[:limite]
