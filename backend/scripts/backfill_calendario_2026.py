"""
Preenche o calendario completo do Brasileirao Serie A 2026 (rodadas 1-38)
como confrontos "agendada" (mandante x visitante, sem data/placar ainda),
usando a lista de jogos que o Victor extraiu da Tabela Detalhada da CBF
(PDF de 17/08/2026) -- sem gastar nenhuma chamada da Highlightly.

So o primeiro turno (rodadas 1-19) foi digitado; o returno (20-38) e
gerado automaticamente invertendo mandante/visitante de cada jogo do
turno 1 (rodada N -> rodada N+19), que e como o Brasileirao sempre
funciona (returno = mesmos confrontos, mando invertido).

Se um confronto (rodada, mandante, visitante) ja existir no banco --
seja porque ja foi importado como finalizada, seja porque ja foi
cadastrado como agendada antes -- o script pula sem sobrescrever nada.
"""

from app.database import SessionLocal
from app.models.time import Time
from app.models.partida import Partida

# "Vasco" no PDF == "Vasco da Gama" no nosso banco.
ALIAS_TIME = {"Vasco": "Vasco da Gama"}

TURNO_1 = {
    1: [
        ("Atlético-MG", "Palmeiras"), ("Internacional", "Athletico-PR"),
        ("Coritiba", "Red Bull Bragantino"), ("Vitória", "Remo"),
        ("Fluminense", "Grêmio"), ("Corinthians", "Bahia"),
        ("Chapecoense", "Santos"), ("São Paulo", "Flamengo"),
        ("Mirassol", "Vasco"), ("Botafogo", "Cruzeiro"),
    ],
    2: [
        ("Flamengo", "Internacional"), ("Red Bull Bragantino", "Atlético-MG"),
        ("Santos", "São Paulo"), ("Remo", "Mirassol"),
        ("Palmeiras", "Vitória"), ("Grêmio", "Botafogo"),
        ("Bahia", "Fluminense"), ("Vasco", "Chapecoense"),
        ("Cruzeiro", "Coritiba"), ("Athletico-PR", "Corinthians"),
    ],
    3: [
        ("Vitória", "Flamengo"), ("Mirassol", "Cruzeiro"),
        ("Chapecoense", "Coritiba"), ("Atlético-MG", "Remo"),
        ("Vasco", "Bahia"), ("São Paulo", "Grêmio"),
        ("Athletico-PR", "Santos"), ("Fluminense", "Botafogo"),
        ("Corinthians", "Red Bull Bragantino"), ("Internacional", "Palmeiras"),
    ],
    4: [
        ("Red Bull Bragantino", "Athletico-PR"), ("Remo", "Internacional"),
        ("Cruzeiro", "Corinthians"), ("Grêmio", "Atlético-MG"),
        ("Palmeiras", "Fluminense"), ("Coritiba", "São Paulo"),
        ("Santos", "Vasco"), ("Bahia", "Chapecoense"),
        ("Botafogo", "Vitória"), ("Flamengo", "Mirassol"),
    ],
    5: [
        ("Mirassol", "Santos"), ("Atlético-MG", "Internacional"),
        ("Bahia", "Vitória"), ("Flamengo", "Cruzeiro"),
        ("Corinthians", "Coritiba"), ("Remo", "Fluminense"),
        ("Vasco", "Palmeiras"), ("São Paulo", "Chapecoense"),
        ("Grêmio", "Red Bull Bragantino"), ("Athletico-PR", "Botafogo"),
    ],
    6: [
        ("Vitória", "Atlético-MG"), ("Botafogo", "Flamengo"),
        ("Fluminense", "Athletico-PR"), ("Santos", "Corinthians"),
        ("Internacional", "Bahia"), ("Palmeiras", "Mirassol"),
        ("Coritiba", "Remo"), ("Red Bull Bragantino", "São Paulo"),
        ("Cruzeiro", "Vasco"), ("Chapecoense", "Grêmio"),
    ],
    7: [
        ("Bahia", "Red Bull Bragantino"), ("Palmeiras", "Botafogo"),
        ("Athletico-PR", "Cruzeiro"), ("Atlético-MG", "São Paulo"),
        ("Mirassol", "Coritiba"), ("Santos", "Internacional"),
        ("Vasco", "Fluminense"), ("Grêmio", "Vitória"),
        ("Flamengo", "Remo"), ("Chapecoense", "Corinthians"),
    ],
    8: [
        ("Red Bull Bragantino", "Botafogo"), ("Fluminense", "Atlético-MG"),
        ("São Paulo", "Palmeiras"), ("Vasco", "Grêmio"),
        ("Cruzeiro", "Santos"), ("Athletico-PR", "Coritiba"),
        ("Remo", "Bahia"), ("Internacional", "Chapecoense"),
        ("Vitória", "Mirassol"), ("Corinthians", "Flamengo"),
    ],
    9: [
        ("Botafogo", "Mirassol"), ("Internacional", "São Paulo"),
        ("Cruzeiro", "Vitória"), ("Bahia", "Athletico-PR"),
        ("Coritiba", "Vasco"), ("Fluminense", "Corinthians"),
        ("Santos", "Remo"), ("Chapecoense", "Atlético-MG"),
        ("Palmeiras", "Grêmio"), ("Red Bull Bragantino", "Flamengo"),
    ],
    10: [
        ("São Paulo", "Cruzeiro"), ("Coritiba", "Fluminense"),
        ("Vasco", "Botafogo"), ("Chapecoense", "Vitória"),
        ("Flamengo", "Santos"), ("Atlético-MG", "Athletico-PR"),
        ("Corinthians", "Internacional"), ("Bahia", "Palmeiras"),
        ("Mirassol", "Red Bull Bragantino"), ("Grêmio", "Remo"),
    ],
    11: [
        ("Vitória", "São Paulo"), ("Remo", "Vasco"),
        ("Mirassol", "Bahia"), ("Santos", "Atlético-MG"),
        ("Internacional", "Grêmio"), ("Athletico-PR", "Chapecoense"),
        ("Botafogo", "Coritiba"), ("Fluminense", "Flamengo"),
        ("Corinthians", "Palmeiras"), ("Cruzeiro", "Red Bull Bragantino"),
    ],
    12: [
        ("Vasco", "São Paulo"), ("Chapecoense", "Botafogo"),
        ("Vitória", "Corinthians"), ("Cruzeiro", "Grêmio"),
        ("Internacional", "Mirassol"), ("Santos", "Fluminense"),
        ("Coritiba", "Atlético-MG"), ("Palmeiras", "Athletico-PR"),
        ("Red Bull Bragantino", "Remo"), ("Flamengo", "Bahia"),
    ],
    13: [
        ("Botafogo", "Internacional"), ("Bahia", "Santos"),
        ("Remo", "Cruzeiro"), ("São Paulo", "Mirassol"),
        ("Corinthians", "Vasco"), ("Grêmio", "Coritiba"),
        ("Red Bull Bragantino", "Palmeiras"), ("Athletico-PR", "Vitória"),
        ("Fluminense", "Chapecoense"), ("Atlético-MG", "Flamengo"),
    ],
    14: [
        ("Botafogo", "Remo"), ("Vitória", "Coritiba"),
        ("Palmeiras", "Santos"), ("Athletico-PR", "Grêmio"),
        ("Cruzeiro", "Atlético-MG"), ("Flamengo", "Vasco"),
        ("São Paulo", "Bahia"), ("Internacional", "Fluminense"),
        ("Chapecoense", "Red Bull Bragantino"), ("Mirassol", "Corinthians"),
    ],
    15: [
        ("Coritiba", "Internacional"), ("Fluminense", "Vitória"),
        ("Bahia", "Cruzeiro"), ("Atlético-MG", "Botafogo"),
        ("Remo", "Palmeiras"), ("Santos", "Red Bull Bragantino"),
        ("Corinthians", "São Paulo"), ("Mirassol", "Chapecoense"),
        ("Grêmio", "Flamengo"), ("Vasco", "Athletico-PR"),
    ],
    16: [
        ("Atlético-MG", "Mirassol"), ("Internacional", "Vasco"),
        ("Fluminense", "São Paulo"), ("Palmeiras", "Cruzeiro"),
        ("Santos", "Coritiba"), ("Botafogo", "Corinthians"),
        ("Bahia", "Grêmio"), ("Red Bull Bragantino", "Vitória"),
        ("Chapecoense", "Remo"), ("Athletico-PR", "Flamengo"),
    ],
    17: [
        ("São Paulo", "Botafogo"), ("Vitória", "Internacional"),
        ("Mirassol", "Fluminense"), ("Grêmio", "Santos"),
        ("Flamengo", "Palmeiras"), ("Cruzeiro", "Chapecoense"),
        ("Remo", "Athletico-PR"), ("Corinthians", "Atlético-MG"),
        ("Vasco", "Red Bull Bragantino"), ("Coritiba", "Bahia"),
    ],
    18: [
        ("Flamengo", "Coritiba"), ("Athletico-PR", "Mirassol"),
        ("Grêmio", "Corinthians"), ("Bahia", "Botafogo"),
        ("Santos", "Vitória"), ("Red Bull Bragantino", "Internacional"),
        ("Vasco", "Atlético-MG"), ("Palmeiras", "Chapecoense"),
        ("Cruzeiro", "Fluminense"), ("Remo", "São Paulo"),
    ],
    19: [
        ("Botafogo", "Santos"), ("Vitória", "Vasco"),
        ("Fluminense", "Red Bull Bragantino"), ("Mirassol", "Grêmio"),
        ("Atlético-MG", "Bahia"), ("Coritiba", "Palmeiras"),
        ("São Paulo", "Athletico-PR"), ("Internacional", "Cruzeiro"),
        ("Chapecoense", "Flamengo"), ("Corinthians", "Remo"),
    ],
}


def nome_time(nome_pdf):
    return ALIAS_TIME.get(nome_pdf, nome_pdf)


def gerar_calendario_completo():
    """Turno 1 (1-19) como veio do PDF + returno (20-38) com mando invertido."""
    calendario = {}
    for rodada, jogos in TURNO_1.items():
        calendario[rodada] = [(nome_time(m), nome_time(v)) for m, v in jogos]
        calendario[rodada + 19] = [(nome_time(v), nome_time(m)) for m, v in jogos]
    return calendario


def backfill():
    db = SessionLocal()
    inseridas = 0
    ja_existiam = 0
    times_faltando = set()

    try:
        times_por_nome = {t.nome: t for t in db.query(Time).all()}
        calendario = gerar_calendario_completo()

        for rodada in sorted(calendario):
            for mandante_nome, visitante_nome in calendario[rodada]:
                time_mandante = times_por_nome.get(mandante_nome)
                time_visitante = times_por_nome.get(visitante_nome)

                if not time_mandante or not time_visitante:
                    for nome in (mandante_nome, visitante_nome):
                        if nome not in times_por_nome:
                            times_faltando.add(nome)
                    continue

                ja_existe = (
                    db.query(Partida)
                    .filter(
                        Partida.rodada == rodada,
                        Partida.time_mandante_id == time_mandante.id,
                        Partida.time_visitante_id == time_visitante.id,
                    )
                    .first()
                )
                if ja_existe:
                    ja_existiam += 1
                    continue

                db.add(Partida(
                    time_mandante_id=time_mandante.id,
                    time_visitante_id=time_visitante.id,
                    status="agendada",
                    rodada=rodada,
                ))
                inseridas += 1

        db.commit()

        print(f"{inseridas} confrontos novos cadastrados como 'agendada' (rodadas 1-38).")
        print(f"{ja_existiam} confrontos ja existiam no banco (nao mexi neles).")
        if times_faltando:
            print(f"ATENCAO -- nomes de time nao encontrados no banco: {sorted(times_faltando)}")
    finally:
        db.close()


if __name__ == "__main__":
    backfill()
