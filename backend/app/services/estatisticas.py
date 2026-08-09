from sqlalchemy import or_
from app.models.partida import Partida

def obter_ultimos_jogos(db, time_id, quantidade=10):
    partidas = (
    db.query(Partida)
    .filter(or_(Partida.time_mandante_id == time_id, Partida.time_visitante_id == time_id))
    .order_by(Partida.data.desc())
    .limit(quantidade)
    .all()
    )

    jogos = []

    for partida in partidas:
        jogou_em_casa = partida.time_mandante_id == time_id

        if jogou_em_casa:
            gols_time = partida.gols_mandante
            gols_adversario = partida.gols_visitante
            adversario = partida.time_visitante.nome
        else:
            gols_time = partida.gols_visitante
            gols_adversario = partida.gols_mandante
            adversario = partida.time_mandante.nome

        if gols_time > gols_adversario:
            resultado = "vitoria"
        elif gols_time == gols_adversario:
            resultado = "empate"
        else:
            resultado = "derrota"

        jogos.append({
            "data": partida.data,
            "adversario": adversario,
            "casa_ou_fora": "casa" if jogou_em_casa else "fora",
            "resultado": resultado,
            "gols_time": gols_time,
            "gols_adversario": gols_adversario,
        })

    return jogos

def calcular_estatisticas(jogos):
    vitorias = sum(1 for jogo in jogos if jogo["resultado"] == "vitoria")
    empates = sum(1 for jogo in jogos if jogo["resultado"] == "empate")
    derrotas = sum(1 for jogo in jogos if jogo["resultado"] == "derrota")
    
    gols_marcados = sum(jogo["gols_time"] for jogo in jogos)
    gols_sofridos = sum(jogo["gols_adversario"] for jogo in jogos)

    total_jogos = len(jogos)
    media_gols = gols_marcados / total_jogos if total_jogos > 0 else 0

    sequencia = [jogo["resultado"] for jogo in jogos]

    return {
        "total_jogos": total_jogos,
        "vitorias": vitorias,
        "empates": empates,
        "derrotas": derrotas,
        "gols_marcados": gols_marcados,
        "gols_sofridos": gols_sofridos,
        "media_gols": round(media_gols, 2),
        "sequencia_recente": sequencia,
    }
