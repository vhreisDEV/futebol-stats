"""
Preenche o placar (so gols_mandante/gols_visitante) das partidas do
primeiro turno que Victor extraiu da Tabela Detalhada da CBF (PDF de
17/08/2026) -- sem estatisticas granulares (escanteios/chutes/cartoes),
que so vem da Highlightly quando a cota renovar.

So atualiza confrontos que ainda estao como 'agendada' (ou seja, nunca
foram importados de verdade pela API) -- se um confronto ja veio da
Highlightly como 'finalizada', ja tem estatisticas completas e melhores
que so o placar do PDF, entao esse script nunca sobrescreve isso (na
pratica isso cobre as rodadas 11-19, que ja vieram completas da API).
"""

from app.database import SessionLocal
from app.models.time import Time
from app.models.partida import Partida

ALIAS_TIME = {"Vasco": "Vasco da Gama"}

# rodada -> [(mandante, visitante, gols_mandante, gols_visitante)]
# "Flamengo x Mirassol" da 4a rodada fica de fora -- consta como
# "a definir" no PDF, ainda sem placar (mantido como esta no banco).
PLACARES = {
    1: [
        ("Atlético-MG", "Palmeiras", 2, 2),
        ("Internacional", "Athletico-PR", 0, 1),
        ("Coritiba", "Red Bull Bragantino", 0, 1),
        ("Vitória", "Remo", 2, 0),
        ("Fluminense", "Grêmio", 2, 1),
        ("Corinthians", "Bahia", 1, 2),
        ("Chapecoense", "Santos", 4, 2),
        ("São Paulo", "Flamengo", 2, 1),
        ("Mirassol", "Vasco", 2, 1),
        ("Botafogo", "Cruzeiro", 4, 0),
    ],
    2: [
        ("Flamengo", "Internacional", 1, 1),
        ("Red Bull Bragantino", "Atlético-MG", 1, 0),
        ("Santos", "São Paulo", 1, 1),
        ("Remo", "Mirassol", 2, 2),
        ("Palmeiras", "Vitória", 5, 1),
        ("Grêmio", "Botafogo", 5, 3),
        ("Bahia", "Fluminense", 1, 1),
        ("Vasco", "Chapecoense", 1, 1),
        ("Cruzeiro", "Coritiba", 1, 2),
        ("Athletico-PR", "Corinthians", 0, 1),
    ],
    3: [
        ("Vitória", "Flamengo", 1, 2),
        ("Mirassol", "Cruzeiro", 2, 2),
        ("Chapecoense", "Coritiba", 3, 3),
        ("Atlético-MG", "Remo", 3, 3),
        ("Vasco", "Bahia", 0, 1),
        ("São Paulo", "Grêmio", 2, 0),
        ("Athletico-PR", "Santos", 2, 1),
        ("Fluminense", "Botafogo", 1, 0),
        ("Corinthians", "Red Bull Bragantino", 2, 0),
        ("Internacional", "Palmeiras", 1, 3),
    ],
    4: [
        ("Red Bull Bragantino", "Athletico-PR", 1, 1),
        ("Remo", "Internacional", 1, 1),
        ("Cruzeiro", "Corinthians", 1, 1),
        ("Grêmio", "Atlético-MG", 2, 1),
        ("Palmeiras", "Fluminense", 2, 1),
        ("Coritiba", "São Paulo", 0, 1),
        ("Santos", "Vasco", 2, 1),
        ("Bahia", "Chapecoense", 2, 0),
        ("Botafogo", "Vitória", 0, 0),
        # ("Flamengo", "Mirassol", ...) -- "a definir" no PDF, sem placar ainda.
    ],
    5: [
        ("Mirassol", "Santos", 2, 2),
        ("Atlético-MG", "Internacional", 1, 0),
        ("Bahia", "Vitória", 1, 1),
        ("Flamengo", "Cruzeiro", 2, 0),
        ("Corinthians", "Coritiba", 0, 2),
        ("Remo", "Fluminense", 0, 2),
        ("Vasco", "Palmeiras", 2, 1),
        ("São Paulo", "Chapecoense", 2, 0),
        ("Grêmio", "Red Bull Bragantino", 1, 1),
        ("Athletico-PR", "Botafogo", 4, 1),
    ],
    6: [
        ("Vitória", "Atlético-MG", 2, 0),
        ("Botafogo", "Flamengo", 0, 3),
        ("Fluminense", "Athletico-PR", 3, 2),
        ("Santos", "Corinthians", 1, 1),
        ("Internacional", "Bahia", 0, 1),
        ("Palmeiras", "Mirassol", 1, 0),
        ("Coritiba", "Remo", 1, 0),
        ("Red Bull Bragantino", "São Paulo", 1, 2),
        ("Cruzeiro", "Vasco", 3, 3),
        ("Chapecoense", "Grêmio", 1, 1),
    ],
    7: [
        ("Bahia", "Red Bull Bragantino", 2, 0),
        ("Palmeiras", "Botafogo", 2, 1),
        ("Athletico-PR", "Cruzeiro", 2, 1),
        ("Atlético-MG", "São Paulo", 1, 0),
        ("Mirassol", "Coritiba", 0, 1),
        ("Santos", "Internacional", 1, 2),
        ("Vasco", "Fluminense", 3, 2),
        ("Grêmio", "Vitória", 2, 0),
        ("Flamengo", "Remo", 3, 0),
        ("Chapecoense", "Corinthians", 0, 0),
    ],
    8: [
        ("Red Bull Bragantino", "Botafogo", 1, 2),
        ("Fluminense", "Atlético-MG", 1, 0),
        ("São Paulo", "Palmeiras", 0, 1),
        ("Vasco", "Grêmio", 2, 1),
        ("Cruzeiro", "Santos", 0, 0),
        ("Athletico-PR", "Coritiba", 2, 0),
        ("Remo", "Bahia", 4, 1),
        ("Internacional", "Chapecoense", 2, 0),
        ("Vitória", "Mirassol", 1, 0),
        ("Corinthians", "Flamengo", 1, 1),
    ],
    9: [
        ("Botafogo", "Mirassol", 3, 2),
        ("Internacional", "São Paulo", 1, 1),
        ("Cruzeiro", "Vitória", 3, 0),
        ("Bahia", "Athletico-PR", 3, 0),
        ("Coritiba", "Vasco", 1, 1),
        ("Fluminense", "Corinthians", 3, 1),
        ("Santos", "Remo", 2, 0),
        ("Chapecoense", "Atlético-MG", 0, 4),
        ("Palmeiras", "Grêmio", 2, 1),
        ("Red Bull Bragantino", "Flamengo", 3, 0),
    ],
    10: [
        ("São Paulo", "Cruzeiro", 4, 1),
        ("Coritiba", "Fluminense", 1, 1),
        ("Vasco", "Botafogo", 1, 2),
        ("Chapecoense", "Vitória", 1, 1),
        ("Flamengo", "Santos", 3, 1),
        ("Atlético-MG", "Athletico-PR", 2, 1),
        ("Corinthians", "Internacional", 0, 1),
        ("Bahia", "Palmeiras", 1, 2),
        ("Mirassol", "Red Bull Bragantino", 0, 1),
        ("Grêmio", "Remo", 0, 0),
    ],
    11: [
        ("Vitória", "São Paulo", 2, 0),
        ("Remo", "Vasco", 1, 1),
        ("Mirassol", "Bahia", 1, 2),
        ("Santos", "Atlético-MG", 1, 0),
        ("Internacional", "Grêmio", 0, 0),
        ("Athletico-PR", "Chapecoense", 2, 0),
        ("Botafogo", "Coritiba", 2, 2),
        ("Fluminense", "Flamengo", 1, 2),
        ("Corinthians", "Palmeiras", 0, 0),
        ("Cruzeiro", "Red Bull Bragantino", 2, 1),
    ],
    12: [
        ("Vasco", "São Paulo", 2, 1),
        ("Chapecoense", "Botafogo", 1, 4),
        ("Vitória", "Corinthians", 0, 0),
        ("Cruzeiro", "Grêmio", 2, 0),
        ("Internacional", "Mirassol", 1, 2),
        ("Santos", "Fluminense", 2, 3),
        ("Coritiba", "Atlético-MG", 2, 0),
        ("Palmeiras", "Athletico-PR", 1, 0),
        ("Red Bull Bragantino", "Remo", 4, 2),
        ("Flamengo", "Bahia", 2, 0),
    ],
    13: [
        ("Botafogo", "Internacional", 2, 2),
        ("Bahia", "Santos", 2, 2),
        ("Remo", "Cruzeiro", 0, 1),
        ("São Paulo", "Mirassol", 1, 0),
        ("Corinthians", "Vasco", 1, 0),
        ("Grêmio", "Coritiba", 1, 0),
        ("Red Bull Bragantino", "Palmeiras", 0, 1),
        ("Athletico-PR", "Vitória", 3, 1),
        ("Fluminense", "Chapecoense", 2, 1),
        ("Atlético-MG", "Flamengo", 0, 4),
    ],
    14: [
        ("Botafogo", "Remo", 1, 2),
        ("Vitória", "Coritiba", 4, 1),
        ("Palmeiras", "Santos", 1, 1),
        ("Athletico-PR", "Grêmio", 0, 0),
        ("Cruzeiro", "Atlético-MG", 1, 3),
        ("Flamengo", "Vasco", 2, 2),
        ("São Paulo", "Bahia", 2, 2),
        ("Internacional", "Fluminense", 2, 0),
        ("Chapecoense", "Red Bull Bragantino", 1, 2),
        ("Mirassol", "Corinthians", 2, 1),
    ],
    15: [
        ("Coritiba", "Internacional", 2, 2),
        ("Fluminense", "Vitória", 2, 2),
        ("Bahia", "Cruzeiro", 1, 2),
        ("Atlético-MG", "Botafogo", 1, 1),
        ("Remo", "Palmeiras", 1, 1),
        ("Santos", "Red Bull Bragantino", 2, 0),
        ("Corinthians", "São Paulo", 3, 2),
        ("Mirassol", "Chapecoense", 1, 1),
        ("Grêmio", "Flamengo", 0, 1),
        ("Vasco", "Athletico-PR", 1, 0),
    ],
    16: [
        ("Atlético-MG", "Mirassol", 3, 1),
        ("Internacional", "Vasco", 4, 1),
        ("Fluminense", "São Paulo", 2, 1),
        ("Palmeiras", "Cruzeiro", 1, 1),
        ("Santos", "Coritiba", 0, 3),
        ("Botafogo", "Corinthians", 3, 1),
        ("Bahia", "Grêmio", 1, 1),
        ("Red Bull Bragantino", "Vitória", 2, 0),
        ("Chapecoense", "Remo", 2, 3),
        ("Athletico-PR", "Flamengo", 1, 1),
    ],
    17: [
        ("São Paulo", "Botafogo", 1, 1),
        ("Vitória", "Internacional", 2, 0),
        ("Mirassol", "Fluminense", 1, 0),
        ("Grêmio", "Santos", 3, 2),
        ("Flamengo", "Palmeiras", 0, 3),
        ("Cruzeiro", "Chapecoense", 2, 1),
        ("Remo", "Athletico-PR", 1, 2),
        ("Corinthians", "Atlético-MG", 1, 0),
        ("Vasco", "Red Bull Bragantino", 0, 3),
        ("Coritiba", "Bahia", 3, 2),
    ],
    18: [
        ("Flamengo", "Coritiba", 3, 0),
        ("Athletico-PR", "Mirassol", 1, 0),
        ("Grêmio", "Corinthians", 1, 3),
        ("Bahia", "Botafogo", 2, 1),
        ("Santos", "Vitória", 3, 1),
        ("Red Bull Bragantino", "Internacional", 3, 1),
        ("Vasco", "Atlético-MG", 0, 1),
        ("Palmeiras", "Chapecoense", 1, 0),
        ("Cruzeiro", "Fluminense", 1, 1),
        ("Remo", "São Paulo", 1, 0),
    ],
    19: [
        ("Botafogo", "Santos", 2, 1),
        ("Vitória", "Vasco", 1, 0),
        ("Fluminense", "Red Bull Bragantino", 1, 1),
        ("Mirassol", "Grêmio", 2, 1),
        ("Atlético-MG", "Bahia", 1, 1),
        ("Coritiba", "Palmeiras", 1, 3),
        ("São Paulo", "Athletico-PR", 1, 2),
        ("Internacional", "Cruzeiro", 1, 2),
        ("Chapecoense", "Flamengo", 0, 4),
        ("Corinthians", "Remo", 3, 0),
    ],
}


def nome_time(nome_pdf):
    return ALIAS_TIME.get(nome_pdf, nome_pdf)


def preencher():
    db = SessionLocal()
    atualizadas = 0
    ja_finalizadas = 0
    nao_encontradas = []

    try:
        times_por_nome = {t.nome: t for t in db.query(Time).all()}

        for rodada, jogos in PLACARES.items():
            for mandante_nome, visitante_nome, gm, gv in jogos:
                time_mandante = times_por_nome.get(nome_time(mandante_nome))
                time_visitante = times_por_nome.get(nome_time(visitante_nome))

                partida = (
                    db.query(Partida)
                    .filter(
                        Partida.rodada == rodada,
                        Partida.time_mandante_id == time_mandante.id,
                        Partida.time_visitante_id == time_visitante.id,
                    )
                    .first()
                )

                if not partida:
                    nao_encontradas.append((rodada, mandante_nome, visitante_nome))
                    continue

                if partida.status == "finalizada":
                    # Ja veio da Highlightly com estatisticas completas --
                    # nao mexe, o placar da API e mais confiavel/completo.
                    ja_finalizadas += 1
                    continue

                partida.status = "finalizada"
                partida.gols_mandante = gm
                partida.gols_visitante = gv
                atualizadas += 1

        db.commit()

        print(f"{atualizadas} partidas atualizadas com o placar do PDF.")
        print(f"{ja_finalizadas} ja estavam finalizadas via API -- nao mexi (mantidas com stats completas).")
        if nao_encontradas:
            print(f"ATENCAO -- confrontos nao encontrados no banco: {nao_encontradas}")
    finally:
        db.close()


if __name__ == "__main__":
    preencher()
