import os

# Gemini (Google AI Studio) tem free tier de verdade, sem cartao de credito
# -- como a analise e' gerada uma vez so por partida e cacheada (ver
# AnaliseIAPartida), o volume real (poucas dezenas de partidas por rodada,
# uma chamada cada, pra sempre) fica bem abaixo do limite gratuito.
MODELO_PADRAO = "gemini-3.6-flash"


class IANaoConfiguradaError(Exception):
    pass


def _formatar_destaque(nome_time, mando_label, d):
    porcentagem = round(d["taxa"] * 100)
    if d["tipo"] == "booleano":
        return f"{nome_time} ({mando_label}): {d['label'].lower()} em {d['acertos']}/{d['total']} jogos ({porcentagem}%)"
    return (
        f"{nome_time} ({mando_label}): passou de {d['linha']} {d['label'].lower()} em "
        f"{d['acertos']}/{d['total']} jogos ({porcentagem}%), média {d['media']}"
    )


def _montar_prompt(partida, destaques_mandante, destaques_visitante):
    mandante = partida.time_mandante.nome
    visitante = partida.time_visitante.nome

    linhas = [
        f"Partida: {mandante} (mandante) x {visitante} (visitante)"
        + (f", rodada {partida.rodada}" if partida.rodada else "")
    ]

    linhas.append("Mercados em que o mandante vem se destacando em casa (últimos jogos):")
    if destaques_mandante:
        linhas += [f"- {_formatar_destaque(mandante, 'em casa', d)}" for d in destaques_mandante]
    else:
        linhas.append("- nenhum mercado com pelo menos 70% de acerto no recorte em casa.")

    linhas.append("Mercados em que o visitante vem se destacando fora de casa (últimos jogos):")
    if destaques_visitante:
        linhas += [f"- {_formatar_destaque(visitante, 'fora de casa', d)}" for d in destaques_visitante]
    else:
        linhas.append("- nenhum mercado com pelo menos 70% de acerto no recorte fora de casa.")

    dados = "\n".join(linhas)

    return (
        "Você é um analista de apostas esportivas experiente. Com base SOMENTE nos dados abaixo "
        "(taxas de acerto reais dos últimos jogos de cada time, já filtrados pelo mando de campo que "
        "cada um vai ter nessa partida), escreva uma análise curta (2 parágrafos, português do Brasil) "
        "apontando qual é o MELHOR mercado pra essa partida e por quê — pode ser um mercado do "
        "mandante, do visitante, ou combinar os dois se fizer sentido (ex.: ambas marcam, se os dois "
        "times tiverem essa tendência). Seja direto e claro, como se estivesse entregando uma dica "
        "pronta pro cliente — não liste os dados brutos como uma tabela. Não invente números que não "
        "estão nos dados, nem informações externas (lesões, escalações, notícias, clima).\n\n"
        f"Dados:\n{dados}"
    )


def gerar_analise(partida, destaques_mandante, destaques_visitante):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise IANaoConfiguradaError()

    from google import genai  # import atrasado -- so precisa resolver se a chave existir

    cliente = genai.Client(api_key=api_key)
    prompt = _montar_prompt(partida, destaques_mandante, destaques_visitante)

    resposta = cliente.models.generate_content(model=MODELO_PADRAO, contents=prompt)
    texto = resposta.text.strip()
    return texto, MODELO_PADRAO
