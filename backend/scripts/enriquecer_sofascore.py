# -*- coding: utf-8 -*-
"""
Enriquece EstatisticaJogadorPartida com chutes/chutes_gol/desarmes/
faltas_cometidas/faltas_sofridas/defesas/minutos_jogados -- campos que a
Highlightly nunca forneceu por jogador (ver [[project_veaga_player_stats_idea]]
na memoria do projeto) -- usando a API interna (nao documentada) do
SofaScore como fonte complementar.

So' ENRIQUECE linhas que ja existem (criadas pelo pipeline da
Highlightly em importar_jogadores.py, que continua sendo a fonte de
verdade pra gols/assistencias/cartoes/aparicao) -- nunca cria Jogador
ou EstatisticaJogadorPartida novo a partir do SofaScore sozinho. So'
atualiza campos que ainda estao None, nunca sobrescreve um valor ja
preenchido (idempotente, seguro rodar de novo).

Bypass do bloqueio anti-bot (confirmado 2026-09-02, ver issue #47):
requests puro leva 403 mesmo com headers de navegador completos --
parece checagem de fingerprint TLS/JA3. curl_cffi com
impersonate="chrome124" contorna sem precisar de headless browser.

Mapeamento de ID (por nome, confirmado 2026-09-02 pro Brasileirao e
2026-09-05 pra Premier League, ver issue #47):
- Liga: CONFIG_LIGA abaixo, uma entrada por campeonato_id nossa com o
  tournament_id/season_id do SofaScore e o mapa de time -- cada liga
  nova precisa entrar aqui (achar o id do torneio/temporada e rodar a
  intersecao de tokens do nome normalizado pra conferir 20/20 sem
  ambiguidade antes de confiar no mapa).
- Time: dentro de CONFIG_LIGA[campeonato_id]["times"], por interseccao
  de tokens do nome normalizado.
- Jogador: dentro do elenco do time ja resolvido (nunca compara contra
  os dois times ao mesmo tempo -- da falso positivo), match por maior
  interseccao de tokens do nome normalizado (sem acento, minusculo).
  Jogador do SofaScore sem nenhum match (score 0) e' ignorado -- pode
  ser reserva que nunca teve minutos em nenhuma partida que ja
  importamos da Highlightly, no' um bug do matching.

Uso (de dentro de backend/; local usa SQLite, ver
enriquecer_sofascore_producao.py pra producao):
    py scripts/enriquecer_sofascore.py <campeonato_id> <numero_da_rodada>
"""
import sys
import unicodedata

from curl_cffi import requests as creq

sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))))

from app.database import SessionLocal
from app.models.time import Time
from app.models.jogador import Jogador
from app.models.partida import Partida
from app.models.estatistica_jogador_partida import EstatisticaJogadorPartida

BASE_URL = "https://api.sofascore.com/api/v1"
IMPERSONATE = "chrome124"

# Uma entrada por campeonato_id nossa (ver app.models.campeonato). Time
# = nosso Time.id -> id do time no SofaScore, confirmado 20/20 por
# intersecao de tokens do nome normalizado (sem excecao manual) antes
# de cada liga entrar aqui.
CONFIG_LIGA = {
    1: {  # Brasileirao Serie A -- confirmado 2026-09-02, ver issue #47
        "tournament_id": 325,
        "season_id": 87678,  # temporada 2026
        "times": {
            1: 5981,     # Flamengo
            2: 1963,     # Palmeiras
            3: 1958,     # Botafogo
            4: 1961,     # Fluminense
            5: 1967,     # Athletico-PR
            6: 1954,     # Cruzeiro
            7: 1955,     # Bahia
            8: 1957,     # Corinthians
            9: 1999,     # Red Bull Bragantino
            10: 1982,    # Coritiba
            11: 1977,    # Atlético-MG
            12: 1981,    # São Paulo
            13: 1962,    # Vitória
            14: 5926,    # Grêmio
            15: 21982,   # Mirassol
            16: 1966,    # Internacional
            17: 1968,    # Santos
            18: 1974,    # Vasco da Gama
            19: 2012,    # Remo
            20: 21845,   # Chapecoense
        },
    },
    2: {  # Premier League -- confirmado 2026-09-05
        "tournament_id": 17,
        "season_id": 96668,  # temporada 26/27
        "times": {
            21: 30,   # Brighton & Hove Albion
            22: 42,   # Arsenal
            23: 50,   # Brentford
            24: 48,   # Everton
            25: 96,   # Hull City
            26: 32,   # Ipswich Town
            27: 17,   # Manchester City
            28: 34,   # Leeds United
            29: 44,   # Liverpool
            30: 39,   # Newcastle United
            31: 38,   # Chelsea
            32: 43,   # Fulham
            33: 60,   # Bournemouth
            34: 41,   # Sunderland
            35: 14,   # Nottingham Forest
            36: 7,    # Crystal Palace
            37: 35,   # Manchester United
            38: 11,   # Coventry City
            39: 33,   # Tottenham Hotspur
            40: 40,   # Aston Villa
        },
    },
    3: {  # La Liga -- confirmado 2026-09-05
        "tournament_id": 8,
        "season_id": 97268,  # temporada 26/27
        "times": {
            41: 2833,  # Sevilla FC -- intersecao de token empatava com "FC Barcelona" (os dois batem so' o token generico "fc"), corrigido a mao
            42: 2885,  # Alavés
            43: 2836,  # Atlético Madrid
            44: 2817,  # Barcelona
            45: 2814,  # Espanyol
            46: 2829,  # Real Madrid
            47: 2816,  # Real Betis
            48: 2859,  # Getafe
            49: 2819,  # Villarreal
            50: 2832,  # Deportivo La Coruña
            51: 2821,  # Celta de Vigo
            52: 2828,  # Valencia
            53: 2835,  # Racing Santander
            54: 2818,  # Rayo Vallecano
            55: 2846,  # Elche
            56: 2820,  # Osasuna
            57: 2824,  # Real Sociedad
            58: 2825,  # Athletic Club
            59: 2830,  # Malaga
            60: 2849,  # Levante
        },
    },
    4: {  # Bundesliga -- confirmado 2026-09-05
        "tournament_id": 35,
        "season_id": 97464,  # temporada 26/27
        "times": {
            61: 2600,   # FC Augsburg
            62: 2681,   # Bayer Leverkusen
            63: 2672,   # Bayern Munich
            64: 2673,   # Borussia Dortmund
            65: 2527,   # Borussia Mönchengladbach -- intersecao empatava com Dortmund (os dois batem so' "borussia"), corrigido a mao
            66: 2674,   # Eintracht Frankfurt
            67: 2598,   # SV Elversberg
            68: 2671,   # FC Koln
            69: 2538,   # SC Freiburg
            70: 2676,   # Hamburger SV
            71: 2569,   # 1899 Hoffenheim
            72: 2556,   # FSV Mainz 05
            73: 2561,   # SC Paderborn 07
            74: 36360,  # RB Leipzig
            75: 2530,   # FC Schalke 04
            76: 2677,   # VfB Stuttgart
            77: 2547,   # Union Berlin
            78: 2534,   # Werder Bremen
        },
    },
    5: {  # Serie A -- confirmado 2026-09-05
        "tournament_id": 23,
        "season_id": 95836,  # temporada 26/27
        "times": {
            79: 2702,  # AS Roma
            80: 2697,  # Inter
            81: 2689,  # Lecce
            82: 2714,  # Napoli
            83: 2692,  # AC Milan
            84: 2686,  # Atalanta
            85: 2719,  # Cagliari
            86: 2687,  # Juventus
            87: 2699,  # Lazio
            88: 2704,  # Como
            89: 2695,  # Udinese
            90: 2793,  # Sassuolo
            91: 2696,  # Torino
            92: 2685,  # Bologna
            93: 2801,  # Frosinone
            94: 2690,  # Parma
            95: 2713,  # Genoa
            96: 2688,  # Venezia
            97: 2729,  # Monza
            98: 2693,  # Fiorentina
        },
    },
    6: {  # Ligue 1 -- confirmado 2026-09-05
        "tournament_id": 34,
        "season_id": 96127,  # temporada 26/27
        "times": {
            99: 1641,   # Marseille
            100: 1648,  # Lens
            101: 1643,  # Lille
            102: 1649,  # Lyon -- SofaScore chama de "Olympique Lyonnais", token "lyon" nao bate direto
            103: 1653,  # Monaco
            104: 1715,  # Stade Brestois 29
            105: 1672,  # Le Mans
            106: 1644,  # Paris Saint Germain -- intersecao empatava com "Paris FC" (os dois batem so' "paris"), corrigido a mao
            107: 1658,  # Rennes FC -- SofaScore chama de "Stade Rennais", nao tinha token em comum nenhum
            108: 1656,  # Lorient
            109: 1661,  # Nice
            110: 6070,  # Paris FC
            111: 1652,  # Estac Troyes
            112: 1662,  # LE Havre AC
            113: 1681,  # Toulouse
            114: 1684,  # Angers
            115: 1646,  # Auxerre
            116: 1659,  # Strasbourg
        },
    },
}

# nome do campo no payload da lineup do SofaScore -> nome do campo em
# EstatisticaJogadorPartida.
MAPA_CAMPOS = {
    "totalShots": "chutes",
    "onTargetScoringAttempt": "chutes_gol",
    "totalTackle": "desarmes",
    "fouls": "faltas_cometidas",
    "wasFouled": "faltas_sofridas",
    "saves": "defesas",
    "minutesPlayed": "minutos_jogados",
}


def normalizar_nome(nome):
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode("ascii")
    return set(sem_acento.lower().split())


def _get(url, params=None):
    resp = creq.get(url, params=params, impersonate=IMPERSONATE, timeout=15)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()


def buscar_eventos_rodada(tournament_id, season_id, rodada):
    dados = _get(f"{BASE_URL}/unique-tournament/{tournament_id}/season/{season_id}/events/round/{rodada}")
    return dados.get("events", []) if dados else []


def buscar_lineups(sofascore_event_id):
    return _get(f"{BASE_URL}/event/{sofascore_event_id}/lineups")


def encontrar_evento(partida, eventos_rodada, time_id_sofascore):
    # Uma partida adiada/remarcada aparece DUAS vezes na listagem da
    # rodada original do SofaScore: o evento adiado original (status
    # "Postponed", sem lineup nenhuma) e o jogo de verdade jogado depois
    # (status "Ended", mesma rodada do SofaScore mesmo se jogado numa
    # data bem posterior) -- confirmado 2026-09-02 em 4 casos reais.
    # Sem essa preferencia, o primeiro da lista (o adiado) ganhava e a
    # partida ficava com 0 jogador enriquecido.
    sofa_mandante = time_id_sofascore.get(partida.time_mandante_id)
    sofa_visitante = time_id_sofascore.get(partida.time_visitante_id)
    if not sofa_mandante or not sofa_visitante:
        return None
    candidatos = [
        evento for evento in eventos_rodada
        if evento["homeTeam"]["id"] == sofa_mandante and evento["awayTeam"]["id"] == sofa_visitante
    ]
    if not candidatos:
        return None
    finalizados = [e for e in candidatos if e["status"]["type"] == "finished"]
    return finalizados[0] if finalizados else candidatos[0]


def casar_jogador(nome_sofa, candidatos):
    """candidatos: lista de Jogador. Compara pelo nome normalizado -- quem
    chama decide o universo de candidatos (ver enriquecer_partida: tem
    que ser quem jogou NESSA partida por ESSE time, nao o time atual do
    jogador, que pode ter mudado por transferencia depois).

    Prefere sempre um match EXATO (conjunto de tokens identico) sobre
    um match parcial -- sem isso, dois jogadores reais com nome parecido
    (ex.: "Erick" e "Erick Pulga" no mesmo time, caso real encontrado
    2026-09-02) empatavam no score de intersecao (ambos batem 1 token
    com "Erick") e o match errado as vezes ganhava por ordem arbitraria.
    Se nao houver match exato e o melhor score parcial empatar entre
    2+ candidatos diferentes, devolve None (ambiguo) em vez de
    adivinhar errado -- melhor deixar sem enriquecer do que enriquecer
    o jogador errado."""
    tokens_sofa = normalizar_nome(nome_sofa)

    exatos = [j for j in candidatos if normalizar_nome(j.nome) == tokens_sofa]
    if len(exatos) == 1:
        return exatos[0]
    if len(exatos) > 1:
        return None  # ambiguo mesmo no exato (nomes duplicados) -- nao adivinha

    pontuados = [(len(tokens_sofa & normalizar_nome(j.nome)), j) for j in candidatos]
    pontuados = [(score, j) for score, j in pontuados if score > 0]
    if not pontuados:
        return None
    melhor_score = max(score for score, _ in pontuados)
    melhores = [j for score, j in pontuados if score == melhor_score]
    return melhores[0] if len(melhores) == 1 else None


def enriquecer_partida(db, partida, evento_sofascore):
    """Enriquece as linhas ja existentes de EstatisticaJogadorPartida dessa
    partida com os campos complementares do SofaScore. So mexe em campo
    que ainda esta None -- nunca sobrescreve. Devolve quantas linhas
    foram atualizadas."""
    lineups = buscar_lineups(evento_sofascore["id"])
    if not lineups:
        return 0

    atualizadas = 0
    for lado, time_id_nosso in (("home", partida.time_mandante_id), ("away", partida.time_visitante_id)):
        # Candidatos = quem JA TEM linha de estatistica nessa partida por
        # esse time -- nao filtra por Jogador.time_id (time ATUAL do
        # jogador), porque um jogador pode ter sido transferido depois
        # dessa partida e Jogador.time_id ja reflete o time novo (bug
        # real encontrado 2026-09-02: goleiro que saiu do Bahia pro
        # Chapecoense sumia do "elenco do Bahia" ao comparar so' pelo
        # time atual, mesmo tendo uma linha de partida antiga do Bahia).
        linhas_do_time = (
            db.query(EstatisticaJogadorPartida)
            .filter(EstatisticaJogadorPartida.partida_id == partida.id, EstatisticaJogadorPartida.time_id == time_id_nosso)
            .all()
        )
        if not linhas_do_time:
            continue
        linhas_por_jogador = {linha.jogador_id: linha for linha in linhas_do_time}
        jogadores_candidatos = db.query(Jogador).filter(Jogador.id.in_(linhas_por_jogador.keys())).all()

        for entrada in lineups.get(lado, {}).get("players", []):
            stats_sofa = entrada.get("statistics")
            if not stats_sofa:
                continue
            jogador = casar_jogador(entrada["player"]["name"], jogadores_candidatos)
            if not jogador:
                continue

            linha = linhas_por_jogador[jogador.id]
            # O SofaScore omite a chave da estatistica inteira quando o valor
            # real e' 0 (confirmado 2026-09-03: Luan Peres jogou os 90 min
            # contra o Vasco e tinha "totalTackle" ausente do payload -- nao
            # e' dado faltando, e' zero desarmes de verdade). So da pra
            # assumir isso quando o jogador realmente jogou (minutesPlayed
            # presente) -- pra quem nao jogou, ausencia de chave nao diz
            # nada (o campo continua None, tratado como "nao jogou" no
            # frontend).
            jogou = stats_sofa.get("minutesPlayed") is not None
            mudou = False
            for campo_sofa, campo_nosso in MAPA_CAMPOS.items():
                if getattr(linha, campo_nosso) is not None:
                    continue
                if campo_sofa in stats_sofa:
                    setattr(linha, campo_nosso, stats_sofa[campo_sofa])
                    mudou = True
                elif jogou and campo_sofa != "minutesPlayed":
                    setattr(linha, campo_nosso, 0)
                    mudou = True
            if mudou:
                atualizadas += 1

    db.commit()
    return atualizadas


def enriquecer_rodada(campeonato_id, rodada):
    config = CONFIG_LIGA.get(campeonato_id)
    if not config:
        print(f"Campeonato {campeonato_id} nao tem CONFIG_LIGA (mapeamento de time/torneio SofaScore) ainda.")
        return

    db = SessionLocal()
    try:
        partidas = (
            db.query(Partida)
            .filter(Partida.campeonato_id == campeonato_id, Partida.rodada == rodada, Partida.status == "finalizada")
            .all()
        )
        if not partidas:
            print(f"Nenhuma partida finalizada encontrada pra rodada {rodada}.")
            return

        eventos_rodada = buscar_eventos_rodada(config["tournament_id"], config["season_id"], rodada)
        print(f"{len(eventos_rodada)} eventos do SofaScore encontrados pra rodada {rodada}.")

        for partida in partidas:
            evento = encontrar_evento(partida, eventos_rodada, config["times"])
            if not evento:
                print(f"  Partida {partida.id} ({partida.time_mandante.nome} x {partida.time_visitante.nome}): "
                      f"evento nao encontrado no SofaScore, pulando.")
                continue
            atualizadas = enriquecer_partida(db, partida, evento)
            print(f"  Partida {partida.id} ({partida.time_mandante.nome} x {partida.time_visitante.nome}): "
                  f"{atualizadas} jogador(es) enriquecido(s).")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: py scripts/enriquecer_sofascore.py <campeonato_id> <numero_da_rodada>")
        sys.exit(1)
    enriquecer_rodada(int(sys.argv[1]), int(sys.argv[2]))
