from sqlalchemy import or_

from app.models.partida import Partida
from app.models.time import Time


def calcular_classificacao(db, ate_rodada=None):
    times = db.query(Time).all()
    tabela = []

    for time in times:
        query = db.query(Partida).filter(
            or_(Partida.time_mandante_id == time.id, Partida.time_visitante_id == time.id),
            Partida.status == "finalizada",
        )
        if ate_rodada is not None:
            query = query.filter(Partida.rodada <= ate_rodada)

        pontos = jogos = vitorias = empates = derrotas = gols_pro = gols_contra = 0

        for partida in query.all():
            jogou_em_casa = partida.time_mandante_id == time.id
            gols_time = partida.gols_mandante if jogou_em_casa else partida.gols_visitante
            gols_adversario = partida.gols_visitante if jogou_em_casa else partida.gols_mandante

            jogos += 1
            gols_pro += gols_time
            gols_contra += gols_adversario

            if gols_time > gols_adversario:
                vitorias += 1
                pontos += 3
            elif gols_time == gols_adversario:
                empates += 1
                pontos += 1
            else:
                derrotas += 1

        tabela.append({
            "time_id": time.id,
            "time": time.nome,
            "pontos": pontos,
            "jogos": jogos,
            "vitorias": vitorias,
            "empates": empates,
            "derrotas": derrotas,
            "gols_pro": gols_pro,
            "gols_contra": gols_contra,
            "saldo_gols": gols_pro - gols_contra,
        })

    # Desempate: pontos, vitorias, saldo de gols, gols pro (nao inclui
    # confronto direto/cartoes, indisponiveis na fonte de dados atual)
    tabela.sort(key=lambda linha: (
        -linha["pontos"],
        -linha["vitorias"],
        -linha["saldo_gols"],
        -linha["gols_pro"],
    ))

    for posicao, linha in enumerate(tabela, start=1):
        linha["posicao"] = posicao

    return tabela
