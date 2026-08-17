"""
Gera jogadores e estatisticas por partida FICTICIOS, só para a gente
visualizar como as telas de /jogadores vao ficar com todos os dados
preenchidos, antes de confirmar como importar os dados reais da
Highlightly. Usa os Times e Partidas REAIS ja no banco (nao inventa
partida nenhuma).

Rode `py scripts/limpar_jogadores_teste.py` para apagar tudo isso
depois, sem afetar Time/Partida.
"""

import random
from app.database import SessionLocal
from app.models.time import Time
from app.models.partida import Partida
from app.models.jogador import Jogador
from app.models.estatistica_jogador_partida import EstatisticaJogadorPartida

PRIMEIROS_NOMES = [
    "Gabriel", "Lucas", "Matheus", "Rafael", "Bruno", "Thiago", "Felipe", "André",
    "Diego", "Vinícius", "Pedro", "João", "Guilherme", "Leonardo", "Rodrigo",
    "Marcos", "Eduardo", "Caio", "Igor", "Renato",
]

SOBRENOMES = [
    "Silva", "Santos", "Oliveira", "Souza", "Costa", "Pereira", "Almeida",
    "Ferreira", "Rodrigues", "Carvalho", "Gomes", "Martins", "Araújo", "Barbosa",
    "Ribeiro", "Cardoso", "Nascimento", "Teixeira", "Moreira", "Lopes",
]

# (posicao, quantidade por time, perfil de stats)
ELENCO = [
    ("Goleiro", 3),
    ("Zagueiro", 5),
    ("Lateral", 4),
    ("Volante", 3),
    ("Meia", 4),
    ("Atacante", 4),
]

PERFIS = {
    "Goleiro": dict(chutes=(0, 0), chutes_gol=(0, 0), desarmes=(0, 1), faltas_c=(0, 1), faltas_s=(0, 1), defesas=(1, 8), gol_chance=0.0, assist_chance=0.0, cartao_chance=0.03),
    "Zagueiro": dict(chutes=(0, 1), chutes_gol=(0, 1), desarmes=(1, 5), faltas_c=(0, 3), faltas_s=(0, 2), defesas=None, gol_chance=0.03, assist_chance=0.01, cartao_chance=0.12),
    "Lateral": dict(chutes=(0, 2), chutes_gol=(0, 1), desarmes=(1, 4), faltas_c=(0, 2), faltas_s=(0, 2), defesas=None, gol_chance=0.02, assist_chance=0.05, cartao_chance=0.1),
    "Volante": dict(chutes=(0, 2), chutes_gol=(0, 1), desarmes=(2, 6), faltas_c=(1, 4), faltas_s=(0, 2), defesas=None, gol_chance=0.02, assist_chance=0.04, cartao_chance=0.15),
    "Meia": dict(chutes=(0, 4), chutes_gol=(0, 2), desarmes=(0, 3), faltas_c=(0, 2), faltas_s=(0, 3), defesas=None, gol_chance=0.08, assist_chance=0.1, cartao_chance=0.08),
    "Atacante": dict(chutes=(1, 6), chutes_gol=(0, 3), desarmes=(0, 1), faltas_c=(0, 2), faltas_s=(0, 3), defesas=None, gol_chance=0.18, assist_chance=0.08, cartao_chance=0.06),
}

JOGADORES_POR_TIME_EM_CAMPO = 14  # 11 titulares + ~3 reservas que entraram


def nome_aleatorio(usados):
    while True:
        nome = f"{random.choice(PRIMEIROS_NOMES)} {random.choice(SOBRENOMES)}"
        if nome not in usados:
            usados.add(nome)
            return nome


def gerar_elenco(db, time):
    usados = set()
    jogadores = []
    for posicao, quantidade in ELENCO:
        for _ in range(quantidade):
            jogador = Jogador(nome=nome_aleatorio(usados), posicao=posicao, time_id=time.id)
            jogadores.append(jogador)
    db.add_all(jogadores)
    db.flush()
    return jogadores


def gerar_stat_linha(jogador, partida, time_id, perfil, titular):
    minutos = random.randint(70, 90) if titular else random.randint(5, 45)
    fator = minutos / 90

    def faixa(intervalo):
        base = random.randint(*intervalo)
        return round(base * fator)

    gol = 1 if random.random() < perfil["gol_chance"] * fator else 0
    assist = 1 if random.random() < perfil["assist_chance"] * fator else 0
    cartao_amarelo = 1 if random.random() < perfil["cartao_chance"] else 0
    cartao_vermelho = 1 if cartao_amarelo and random.random() < 0.05 else 0
    defesas = faixa(perfil["defesas"]) if perfil["defesas"] is not None else None

    return EstatisticaJogadorPartida(
        jogador_id=jogador.id,
        partida_id=partida.id,
        time_id=time_id,
        minutos_jogados=minutos,
        gols=gol,
        assistencias=assist,
        chutes=faixa(perfil["chutes"]),
        chutes_gol=min(faixa(perfil["chutes_gol"]), faixa(perfil["chutes"])),
        desarmes=faixa(perfil["desarmes"]),
        faltas_cometidas=faixa(perfil["faltas_c"]),
        faltas_sofridas=faixa(perfil["faltas_s"]),
        defesas=defesas,
        cartoes_amarelos=cartao_amarelo,
        cartoes_vermelhos=cartao_vermelho,
    )


def seed():
    db = SessionLocal()
    try:
        if db.query(Jogador).count() > 0:
            print("Ja existem jogadores no banco. Rode limpar_jogadores_teste.py antes de gerar de novo.")
            return

        times = db.query(Time).all()
        elenco_por_time = {time.id: gerar_elenco(db, time) for time in times}
        db.commit()

        partidas = db.query(Partida).all()
        linhas = []

        for partida in partidas:
            for time_id in (partida.time_mandante_id, partida.time_visitante_id):
                elenco = elenco_por_time.get(time_id, [])
                if not elenco:
                    continue
                em_campo = random.sample(elenco, min(JOGADORES_POR_TIME_EM_CAMPO, len(elenco)))
                for indice, jogador in enumerate(em_campo):
                    titular = indice < 11
                    perfil = PERFIS[jogador.posicao]
                    linhas.append(gerar_stat_linha(jogador, partida, time_id, perfil, titular))

        db.add_all(linhas)
        db.commit()

        print(f"Seed de teste concluido: {sum(len(v) for v in elenco_por_time.values())} jogadores, "
              f"{len(linhas)} linhas de estatistica em {len(partidas)} partidas.")
        print("Isso e dado FICTICIO so para visualizar as telas -- rode limpar_jogadores_teste.py antes de importar dados reais.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
