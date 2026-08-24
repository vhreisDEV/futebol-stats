from datetime import date

from app.services.gols_esperados import calcular_gols_esperados
from app.services.probabilidade_resultado import calcular_probabilidade_resultado
from app.services.escanteios_esperados import calcular_escanteios_esperados
from app.services.cartoes_esperados import calcular_cartoes_esperados

# Notas de 0 a 10 calculadas direto das nossas estatisticas (nao pela IA) --
# instantaneo, gratis e sempre consistente. Os limites min/max de cada
# escala foram escolhidos a partir da faixa tipica observada no
# Brasileirao (nao sao um padrao estatistico formal, so uma régua pra
# posicionar visualmente o numero).


def _escala(valor, minimo, maximo):
    if valor is None:
        return None
    normalizado = (valor - minimo) / (maximo - minimo)
    return round(max(0.0, min(10.0, normalizado * 10)), 1)


def calcular_notas_partida(db, partida):
    referencia = partida.data or date.today()
    mandante_id = partida.time_mandante_id
    visitante_id = partida.time_visitante_id

    gols = calcular_gols_esperados(db, mandante_id, visitante_id, referencia)
    resultado = calcular_probabilidade_resultado(db, mandante_id, visitante_id, referencia)
    escanteios = calcular_escanteios_esperados(db, mandante_id, visitante_id, referencia)
    cartoes = calcular_cartoes_esperados(db, mandante_id, visitante_id, referencia)

    p_mandante = resultado.get("probabilidade_vitoria_mandante")
    p_visitante = resultado.get("probabilidade_vitoria_visitante")
    equilibrio = None
    if p_mandante is not None and p_visitante is not None:
        diferenca = abs(p_mandante - p_visitante)
        equilibrio = round(max(0.0, 10 - (diferenca / 10)), 1)

    poder_mandante = _escala(gols.get("gols_esperados_mandante"), 0.3, 2.5)
    poder_visitante = _escala(gols.get("gols_esperados_visitante"), 0.3, 2.5)

    intensidade = None
    cartoes_total = cartoes.get("total_cartoes_esperado")
    escanteios_total = escanteios.get("total_esperado")
    if cartoes_total is not None and escanteios_total is not None:
        nota_cartoes = _escala(cartoes_total, 2, 7)
        nota_escanteios = _escala(escanteios_total, 6, 12)
        intensidade = round((nota_cartoes + nota_escanteios) / 2, 1)

    # "Confianca": quantos jogos de historico (janela de 10) sustentam a
    # projecao -- ja fica naturalmente numa escala 0-10. Penaliza se um dos
    # times precisou cair pro fallback de forma geral (sem separar
    # casa/fora), porque ai a projecao usa um dado menos especifico.
    detalhe_mandante = gols.get("detalhe_mandante") or {}
    detalhe_visitante = gols.get("detalhe_visitante") or {}
    jogos_mandante = detalhe_mandante.get("jogos_considerados", 0)
    jogos_visitante = detalhe_visitante.get("jogos_considerados", 0)
    confianca = round((jogos_mandante + jogos_visitante) / 2, 1)
    if detalhe_mandante.get("fallback_para_geral") or detalhe_visitante.get("fallback_para_geral"):
        confianca = round(max(0.0, confianca - 1.5), 1)

    return {
        "equilibrio": equilibrio,
        "poder_ofensivo_mandante": poder_mandante,
        "poder_ofensivo_visitante": poder_visitante,
        "intensidade": intensidade,
        "confianca": confianca,
    }
