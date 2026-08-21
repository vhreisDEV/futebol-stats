"""
Testes da logica de linha/taxa de acerto em app/services/destaques.py --
nao mexe em banco, so cobre as funcoes puras (_encontrar_destaques e os
extratores de serie), que sao onde um erro de metodologia passaria batido
silenciosamente (foi exatamente o que aconteceu com o bug historico
"linha = media", que fazia toda stat bater ~50% e retornar vazio sempre).
"""

from app.services.destaques import (
    MINIMO_JOGOS,
    TAXA_MINIMA_DESTAQUE,
    _encontrar_destaques,
    _serie_ambas_marcam,
    _serie_campo,
    _serie_sem_perder,
)


def _stat_numerica(chave="chutes", linhas=(0.5, 1.5, 2.5, 3.5)):
    return {"chave": chave, "label": chave, "tipo": "quantidade", "linhas": list(linhas), "extrator": _serie_campo(chave)}


def _perspectivas(valores, campo="chutes"):
    return [{campo: v} for v in valores]


def test_serie_com_taxa_alta_qualifica():
    # 8 de 10 acima da linha 0.5 -> 80%, bate o minimo de 70%
    valores = [1, 1, 1, 1, 1, 1, 1, 1, 0, 0]
    destaques = _encontrar_destaques(_perspectivas(valores), [_stat_numerica(linhas=[0.5])])

    assert len(destaques) == 1
    assert destaques[0]["linha"] == 0.5
    assert destaques[0]["acertos"] == 8
    assert destaques[0]["total"] == 10
    assert destaques[0]["taxa"] == 0.8


def test_taxa_abaixo_do_minimo_nao_qualifica():
    # 6 de 10 -> 60%, abaixo do TAXA_MINIMA_DESTAQUE (70%)
    valores = [1, 1, 1, 1, 1, 1, 0, 0, 0, 0]
    destaques = _encontrar_destaques(_perspectivas(valores), [_stat_numerica(linhas=[0.5])])

    assert destaques == []


def test_taxa_exatamente_no_limite_qualifica():
    # 7 de 10 -> exatamente 70%, deve qualificar (>=, nao >)
    valores = [1, 1, 1, 1, 1, 1, 1, 0, 0, 0]
    destaques = _encontrar_destaques(_perspectivas(valores), [_stat_numerica(linhas=[0.5])])

    assert len(destaques) == 1
    assert destaques[0]["taxa"] == 0.7


def test_amostra_menor_que_minimo_jogos_nao_qualifica():
    # so 4 jogos, mesmo que 100% dos valores passem da linha
    valores = [5, 5, 5, 5]
    assert len(valores) < MINIMO_JOGOS

    destaques = _encontrar_destaques(_perspectivas(valores), [_stat_numerica(linhas=[0.5])])
    assert destaques == []


def test_linha_igual_a_media_nao_garante_destaque():
    """Regressao do bug historico: testar contra `linha = media` faz a
    taxa de acerto ficar perto de 50% por definicao (e' o que uma media
    e'), entao nunca deveria realmente qualificar. Aqui a media da serie
    e' 2.0 -- testando contra a linha 2.5 fixa (ligeiramente acima da
    media), so metade dos jogos passa, e nao deve qualificar."""
    valores = [3, 1, 3, 1, 3, 1, 3, 1, 3, 1]  # media = 2.0
    destaques = _encontrar_destaques(_perspectivas(valores), [_stat_numerica(linhas=[2.5])])

    assert destaques == []


def test_escolhe_a_linha_mais_alta_entre_as_qualificantes():
    # bate 90% na linha 0.5 e tambem 70% na linha 1.5 -- deve ficar com a 1.5 (mais especifica)
    valores = [2, 2, 2, 2, 2, 2, 2, 0, 1, 1]
    destaques = _encontrar_destaques(_perspectivas(valores), [_stat_numerica(linhas=[0.5, 1.5, 2.5])])

    assert len(destaques) == 1
    assert destaques[0]["linha"] == 1.5


def test_ordena_por_taxa_decrescente_entre_stats_diferentes():
    perspectivas = [{"a": v_a, "b": v_b} for v_a, v_b in zip(
        [1] * 7 + [0] * 3,  # 70% (a)
        [1] * 9 + [0],  # 90% (b)
    )]
    stats = [_stat_numerica("a", linhas=[0.5]), _stat_numerica("b", linhas=[0.5])]

    destaques = _encontrar_destaques(perspectivas, stats)

    assert [d["stat"] for d in destaques] == ["b", "a"]


def test_serie_ambas_marcam_booleana():
    perspectivas = [
        {"gols_marcados": 2, "gols_sofridos": 1},  # ambas marcam
        {"gols_marcados": 0, "gols_sofridos": 1},  # so um marca
        {"gols_marcados": 1, "gols_sofridos": 1},
        {"gols_marcados": 1, "gols_sofridos": 0},
        {"gols_marcados": 2, "gols_sofridos": 2},
        {"gols_marcados": 1, "gols_sofridos": 3},
        {"gols_marcados": 0, "gols_sofridos": 0},
        {"gols_marcados": 1, "gols_sofridos": 1},
        {"gols_marcados": 3, "gols_sofridos": 1},
        {"gols_marcados": 1, "gols_sofridos": 2},
    ]
    stat = {"chave": "ambas_marcam", "label": "Ambas marcam", "tipo": "booleano", "linhas": [0.5], "extrator": _serie_ambas_marcam}

    destaques = _encontrar_destaques(perspectivas, [stat])

    assert len(destaques) == 1
    assert destaques[0]["sequencia"] == [1, 0, 1, 0, 1, 1, 0, 1, 1, 1]
    assert destaques[0]["acertos"] == 7
    assert destaques[0]["taxa"] == 0.7


def test_serie_sem_perder_booleana():
    perspectivas = [{"gols_marcados": gm, "gols_sofridos": gs} for gm, gs in [
        (2, 1), (1, 1), (0, 2), (3, 0), (1, 1), (2, 2), (0, 1), (1, 0), (2, 0), (1, 1),
    ]]
    stat = {"chave": "sem_perder", "label": "Nao perde", "tipo": "booleano", "linhas": [0.5], "extrator": _serie_sem_perder}

    destaques = _encontrar_destaques(perspectivas, [stat])

    assert len(destaques) == 1
    assert destaques[0]["acertos"] == 8  # (0, 2) e (0, 1) sao as 2 derrotas
    assert destaques[0]["taxa"] == 0.8


def test_extrator_ignora_valores_none():
    # campo ausente em alguns jogos (ex.: escanteios nao importado ainda) nao conta na amostra
    perspectivas = [{"chutes": v} for v in [5, 5, None, 5, 5, None, 5, 5, 5, 5]]
    destaques = _encontrar_destaques(perspectivas, [_stat_numerica(linhas=[0.5])])

    assert len(destaques) == 1
    assert destaques[0]["total"] == 8  # os 2 None nao contam
