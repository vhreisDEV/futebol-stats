import os
from datetime import date

from app.services.gols_esperados import calcular_gols_esperados
from app.services.placar_mais_provavel import calcular_placares_mais_provaveis
from app.services.probabilidade_resultado import calcular_probabilidade_resultado
from app.services.escanteios_esperados import calcular_escanteios_esperados
from app.services.cartoes_esperados import calcular_cartoes_esperados

# Gemini (Google AI Studio) tem free tier de verdade, sem cartao de credito
# -- como a analise e' gerada uma vez so por partida e cacheada (ver
# AnaliseIAPartida), o volume real (poucas dezenas de partidas por rodada,
# uma chamada cada, pra sempre) fica bem abaixo do limite gratuito.
MODELO_PADRAO = "gemini-2.5-flash"


class IANaoConfiguradaError(Exception):
    pass


def _montar_prompt(db, partida):
    mandante = partida.time_mandante.nome
    visitante = partida.time_visitante.nome
    referencia = partida.data or date.today()

    gols = calcular_gols_esperados(db, partida.time_mandante_id, partida.time_visitante_id, referencia)
    resultado = calcular_probabilidade_resultado(db, partida.time_mandante_id, partida.time_visitante_id, referencia)
    placares = calcular_placares_mais_provaveis(
        gols.get("gols_esperados_mandante"), gols.get("gols_esperados_visitante")
    )
    escanteios = calcular_escanteios_esperados(db, partida.time_mandante_id, partida.time_visitante_id, referencia)
    cartoes = calcular_cartoes_esperados(db, partida.time_mandante_id, partida.time_visitante_id, referencia)

    linhas = [
        f"Partida: {mandante} (mandante) x {visitante} (visitante)"
        + (f", rodada {partida.rodada}" if partida.rodada else ""),
        f"Gols esperados: {mandante} {gols.get('gols_esperados_mandante')}, "
        f"{visitante} {gols.get('gols_esperados_visitante')}",
        f"Probabilidades de resultado: vitoria {mandante} {resultado.get('probabilidade_vitoria_mandante')}%, "
        f"empate {resultado.get('probabilidade_empate')}%, "
        f"vitoria {visitante} {resultado.get('probabilidade_vitoria_visitante')}%",
    ]
    if placares:
        top = placares[0]
        linhas.append(
            f"Placar mais provavel: {top['gols_mandante']}-{top['gols_visitante']} ({top['probabilidade']}%)"
        )
    if escanteios.get("total_esperado") is not None:
        linhas.append(
            f"Escanteios esperados no total: {escanteios.get('total_esperado')} "
            f"(tendencia: {escanteios.get('tendencia')})"
        )
    if cartoes.get("total_cartoes_esperado") is not None:
        linhas.append(
            f"Cartoes esperados no total: {cartoes.get('total_cartoes_esperado')} "
            f"(tendencia: {cartoes.get('tendencia')})"
        )

    dados = "\n".join(linhas)

    return (
        "Voce e um analista esportivo experiente escrevendo uma previa curta (2 a 3 paragrafos, "
        "em portugues do Brasil) para uma partida de futebol, com base apenas nos dados estatisticos "
        "abaixo. Escreva como um texto editorial natural e fluido -- nunca liste os dados brutos como "
        "uma tabela. Nao invente informacoes que nao estao nos dados (lesoes, escalacoes, noticias, "
        "clima); baseie-se so no que foi fornecido.\n\n"
        f"Dados:\n{dados}"
    )


def gerar_analise(db, partida):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise IANaoConfiguradaError()

    from google import genai  # import atrasado -- so precisa resolver se a chave existir

    cliente = genai.Client(api_key=api_key)
    prompt = _montar_prompt(db, partida)

    resposta = cliente.models.generate_content(model=MODELO_PADRAO, contents=prompt)
    texto = resposta.text.strip()
    return texto, MODELO_PADRAO
