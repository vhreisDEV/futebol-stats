import os

# Gemini (Google AI Studio) tem free tier de verdade, sem cartao de credito
# -- como a analise e' gerada uma vez so por partida e cacheada (ver
# AnaliseIAPartida), o volume real (poucas dezenas de partidas por rodada,
# uma chamada cada, pra sempre) fica bem abaixo do limite gratuito.
MODELO_PADRAO = "gemini-3.6-flash"


class IANaoConfiguradaError(Exception):
    pass


def _mando_label(perna):
    return "em casa" if perna["time"] == "mandante" else "fora de casa"


def _descrever_perna(perna):
    d = perna["destaque"]
    porcentagem = round(d["taxa"] * 100)
    if d["tipo"] == "booleano":
        return f"{perna['nome_time']} ({_mando_label(perna)}): {d['label'].lower()} em {porcentagem}% dos últimos jogos"
    return (
        f"{perna['nome_time']} ({_mando_label(perna)}): mais de {d['linha']} {d['label'].lower()} "
        f"em {porcentagem}% dos últimos jogos"
    )


def _montar_prompt(bilhete_simples, bilhete_multipla):
    linhas = []
    if bilhete_simples:
        linhas.append(f"Bilhete simples sugerido: {_descrever_perna(bilhete_simples['perna'])}")
    if bilhete_multipla:
        for p in bilhete_multipla["pernas"]:
            linhas.append(f"Perna da múltipla: {_descrever_perna(p)}")

    dados = "\n".join(linhas)

    return (
        "Você é um analista de apostas esportivas. Com base SOMENTE nos dados abaixo, escreva UMA "
        "frase curta (no máximo 25 palavras, português do Brasil, direta e didática) validando por "
        "que esse bilhete faz sentido. Não repita os números (eles já aparecem na tela) — só o "
        "raciocínio central. Não invente dados que não estão aqui.\n\n"
        f"Dados:\n{dados}"
    )


def gerar_analise(bilhete_simples, bilhete_multipla):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise IANaoConfiguradaError()

    from google import genai  # import atrasado -- so precisa resolver se a chave existir

    cliente = genai.Client(api_key=api_key)
    prompt = _montar_prompt(bilhete_simples, bilhete_multipla)

    resposta = cliente.models.generate_content(model=MODELO_PADRAO, contents=prompt)
    texto = resposta.text.strip()
    return texto, MODELO_PADRAO


def _descrever_perna_total(perna):
    # Mercado de "totais do jogo" soma os dois times -- descrever como
    # "[time] (mando): mais de X [stat]" lia como se fosse so daquele
    # time (feedback real de usuario), entao aqui a frase deixa explicito
    # que e' a partida inteira.
    d = perna["destaque"]
    porcentagem = round(d["taxa"] * 100)
    stat = d["label"].replace(" totais no jogo", "").lower()
    return (
        f"Jogos com {perna['nome_time']} {_mando_label(perna)} costumam ter mais de {d['linha']} {stat} "
        f"no total somando os dois times, em {porcentagem}% dos últimos jogos"
    )


def _montar_prompt_dicas(pernas_totais):
    linhas = [f"- {_descrever_perna_total(p)}" for p in pernas_totais]
    dados = "\n".join(linhas)

    return (
        "Você é um analista de apostas esportivas. Com base SOMENTE nos dados abaixo sobre totais "
        "do jogo (soma dos dois times em chutes, escanteios ou cartões -- não é a estatística de um "
        "time isolado), escreva de 2 a 3 dicas curtas em português do Brasil, no estilo 'fique de "
        "olho no total de chutes: costuma passar de X quando [time] joga em casa/fora'. Deixe claro "
        "em cada dica que o número é a soma dos dois times, não só de um lado. Uma dica por linha, "
        "direto, sem repetir os números crus. Não invente dados que não estão aqui.\n\n"
        f"Dados:\n{dados}"
    )


def gerar_dicas(pernas_totais):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise IANaoConfiguradaError()
    if not pernas_totais:
        return None, MODELO_PADRAO

    from google import genai  # import atrasado -- so precisa resolver se a chave existir

    cliente = genai.Client(api_key=api_key)
    prompt = _montar_prompt_dicas(pernas_totais)

    resposta = cliente.models.generate_content(model=MODELO_PADRAO, contents=prompt)
    texto = resposta.text.strip()
    return texto, MODELO_PADRAO
