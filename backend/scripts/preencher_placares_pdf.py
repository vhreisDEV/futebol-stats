"""
Preenche o placar (so gols_mandante/gols_visitante) das partidas do
primeiro turno que Victor extraiu da Tabela Detalhada da CBF (PDF de
17/08/2026) -- sem estatisticas granulares (escanteios/chutes/cartoes),
que so vem da Highlightly quando a cota renovar.

So atualiza confrontos que ainda estao como 'agendada' (ou seja, nunca
foram importados de verdade pela API) -- se um confronto ja veio da
Highlightly como 'finalizada', ja tem estatisticas completas e melhores
que so o placar do PDF, entao esse script nunca sobrescreve isso.
"""

from app.database import SessionLocal
from app.models.time import Time
from app.models.partida import Partida

ALIAS_TIME = {"Vasco": "Vasco da Gama"}

# rodada -> [(mandante, visitante, gols_mandante, gols_visitante)]
# "Flamengo x Mirassol" da 4a rodada fica de fora -- consta como "A def."
# no PDF, ainda sem placar definido (mantido como esta no banco).
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

        print(f"{atualizadas} partidas atualizadas com o placar do PDF (rodadas 1-2, so gols).")
        print(f"{ja_finalizadas} ja estavam finalizadas via API -- nao mexi (mantidas com stats completas).")
        if nao_encontradas:
            print(f"ATENCAO -- confrontos nao encontrados no banco: {nao_encontradas}")
    finally:
        db.close()


if __name__ == "__main__":
    preencher()
