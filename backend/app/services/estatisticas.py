from sqlalchemy import or_
from app.models.partida import Partida


def _filtro_mando(time_id, mando):
    if mando == "casa":
        return Partida.time_mandante_id == time_id
    if mando == "fora":
        return Partida.time_visitante_id == time_id
    return or_(Partida.time_mandante_id == time_id, Partida.time_visitante_id == time_id)


def obter_ultimos_jogos(db, time_id, quantidade=10, mando=None):
    partidas = (
        db.query(Partida)
        .filter(_filtro_mando(time_id, mando))
        .order_by(Partida.data.desc())
        .limit(quantidade)
        .all()
    )

    return [_montar_jogo(partida, time_id) for partida in partidas]


def obter_jogos_ate_rodada(db, time_id, rodada):
    partidas = (
        db.query(Partida)
        .filter(
            or_(Partida.time_mandante_id == time_id, Partida.time_visitante_id == time_id),
            Partida.rodada <= rodada,
        )
        .order_by(Partida.data.desc())
        .all()
    )

    return [_montar_jogo(partida, time_id) for partida in partidas]


def _montar_jogo(partida, time_id):
    jogou_em_casa = partida.time_mandante_id == time_id

    if jogou_em_casa:
        gols_time = partida.gols_mandante
        gols_adversario = partida.gols_visitante
        adversario = partida.time_visitante.nome
        escanteios_time = partida.escanteios_mandante
        escanteios_adversario = partida.escanteios_visitante
        escanteios_1t_time = partida.escanteios_1t_mandante
        escanteios_1t_adversario = partida.escanteios_1t_visitante
        escanteios_2t_time = partida.escanteios_2t_mandante
        escanteios_2t_adversario = partida.escanteios_2t_visitante
        chutes_time = partida.chutes_mandante
        chutes_adversario = partida.chutes_visitante
        chutes_1t_time = partida.chutes_1t_mandante
        chutes_1t_adversario = partida.chutes_1t_visitante
        chutes_gol_time = partida.chutes_gol_mandante
        chutes_gol_adversario = partida.chutes_gol_visitante
        cartoes_amarelos_time = partida.cartoes_amarelos_mandante
        cartoes_amarelos_adversario = partida.cartoes_amarelos_visitante
        cartoes_vermelhos_time = partida.cartoes_vermelhos_mandante
        cartoes_vermelhos_adversario = partida.cartoes_vermelhos_visitante
    else:
        gols_time = partida.gols_visitante
        gols_adversario = partida.gols_mandante
        adversario = partida.time_mandante.nome
        escanteios_time = partida.escanteios_visitante
        escanteios_adversario = partida.escanteios_mandante
        escanteios_1t_time = partida.escanteios_1t_visitante
        escanteios_1t_adversario = partida.escanteios_1t_mandante
        escanteios_2t_time = partida.escanteios_2t_visitante
        escanteios_2t_adversario = partida.escanteios_2t_mandante
        chutes_time = partida.chutes_visitante
        chutes_adversario = partida.chutes_mandante
        chutes_1t_time = partida.chutes_1t_visitante
        chutes_1t_adversario = partida.chutes_1t_mandante
        chutes_gol_time = partida.chutes_gol_visitante
        chutes_gol_adversario = partida.chutes_gol_mandante
        cartoes_amarelos_time = partida.cartoes_amarelos_visitante
        cartoes_amarelos_adversario = partida.cartoes_amarelos_mandante
        cartoes_vermelhos_time = partida.cartoes_vermelhos_visitante
        cartoes_vermelhos_adversario = partida.cartoes_vermelhos_mandante

    if gols_time > gols_adversario:
        resultado = "vitoria"
    elif gols_time == gols_adversario:
        resultado = "empate"
    else:
        resultado = "derrota"

    return {
        "id": partida.id,
        "data": partida.data,
        "adversario": adversario,
        "casa_ou_fora": "casa" if jogou_em_casa else "fora",
        "resultado": resultado,
        "gols_time": gols_time,
        "gols_adversario": gols_adversario,
        "escanteios_time": escanteios_time,
        "escanteios_adversario": escanteios_adversario,
        "escanteios_1t_time": escanteios_1t_time,
        "escanteios_1t_adversario": escanteios_1t_adversario,
        "escanteios_2t_time": escanteios_2t_time,
        "escanteios_2t_adversario": escanteios_2t_adversario,
        "chutes_time": chutes_time,
        "chutes_adversario": chutes_adversario,
        "chutes_1t_time": chutes_1t_time,
        "chutes_1t_adversario": chutes_1t_adversario,
        "chutes_gol_time": chutes_gol_time,
        "chutes_gol_adversario": chutes_gol_adversario,
        "cartoes_amarelos_time": cartoes_amarelos_time,
        "cartoes_amarelos_adversario": cartoes_amarelos_adversario,
        "cartoes_vermelhos_time": cartoes_vermelhos_time,
        "cartoes_vermelhos_adversario": cartoes_vermelhos_adversario,
    }


def calcular_estatisticas(jogos):
    vitorias = sum(1 for jogo in jogos if jogo["resultado"] == "vitoria")
    empates = sum(1 for jogo in jogos if jogo["resultado"] == "empate")
    derrotas = sum(1 for jogo in jogos if jogo["resultado"] == "derrota")

    gols_marcados = sum(jogo["gols_time"] for jogo in jogos)
    gols_sofridos = sum(jogo["gols_adversario"] for jogo in jogos)

    total_jogos = len(jogos)
    media_gols = gols_marcados / total_jogos if total_jogos > 0 else 0

    def media(chave):
        if total_jogos == 0:
            return 0
        return round(sum(jogo[chave] for jogo in jogos) / total_jogos, 2)

    sequencia = [jogo["resultado"] for jogo in jogos]

    return {
        "total_jogos": total_jogos,
        "vitorias": vitorias,
        "empates": empates,
        "derrotas": derrotas,
        "gols_marcados": gols_marcados,
        "gols_sofridos": gols_sofridos,
        "media_gols": round(media_gols, 2),
        "media_escanteios": media("escanteios_time"),
        "media_chutes": media("chutes_time"),
        "media_chutes_gol": media("chutes_gol_time"),
        "media_cartoes_amarelos": media("cartoes_amarelos_time"),
        "media_cartoes_vermelhos": media("cartoes_vermelhos_time"),
        "sequencia_recente": sequencia,
    }