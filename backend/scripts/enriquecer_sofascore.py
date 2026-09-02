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

Mapeamento de ID (por nome, confirmado 2026-09-02, ver issue #47):
- Time: TIME_ID_SOFASCORE abaixo, fixo pros 20 times do Brasileirao
  2026 (interseccao de tokens do nome normalizado bateu 20/20 sem
  excecao manual -- ver script de teste na issue #47).
- Jogador: dentro do elenco do time ja resolvido (nunca compara contra
  os dois times ao mesmo tempo -- da falso positivo), match por maior
  interseccao de tokens do nome normalizado (sem acento, minusculo).
  Jogador do SofaScore sem nenhum match (score 0) e' ignorado -- pode
  ser reserva que nunca teve minutos em nenhuma partida que ja
  importamos da Highlightly, no' um bug do matching.

Uso (de dentro de backend/; local usa SQLite, ver
enriquecer_sofascore_producao.py pra producao):
    py scripts/enriquecer_sofascore.py <numero_da_rodada>
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

SOFASCORE_TOURNAMENT_ID = 325  # Brasileirao Serie A
SOFASCORE_SEASON_ID = 87678  # temporada 2026

# nosso Time.id -> id do time no SofaScore -- confirmado 20/20 por
# intersecao de tokens do nome normalizado, 2026-09-02 (ver issue #47).
TIME_ID_SOFASCORE = {
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
}
SOFASCORE_ID_PARA_TIME_ID = {v: k for k, v in TIME_ID_SOFASCORE.items()}

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


def buscar_eventos_rodada(rodada):
    dados = _get(f"{BASE_URL}/unique-tournament/{SOFASCORE_TOURNAMENT_ID}/season/{SOFASCORE_SEASON_ID}/events/round/{rodada}")
    return dados.get("events", []) if dados else []


def buscar_lineups(sofascore_event_id):
    return _get(f"{BASE_URL}/event/{sofascore_event_id}/lineups")


def encontrar_evento(partida, eventos_rodada):
    # Uma partida adiada/remarcada aparece DUAS vezes na listagem da
    # rodada original do SofaScore: o evento adiado original (status
    # "Postponed", sem lineup nenhuma) e o jogo de verdade jogado depois
    # (status "Ended", mesma rodada do SofaScore mesmo se jogado numa
    # data bem posterior) -- confirmado 2026-09-02 em 4 casos reais.
    # Sem essa preferencia, o primeiro da lista (o adiado) ganhava e a
    # partida ficava com 0 jogador enriquecido.
    sofa_mandante = TIME_ID_SOFASCORE.get(partida.time_mandante_id)
    sofa_visitante = TIME_ID_SOFASCORE.get(partida.time_visitante_id)
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
    jogador, que pode ter mudado por transferencia depois)."""
    tokens_sofa = normalizar_nome(nome_sofa)
    melhor = None
    melhor_score = 0
    for jogador in candidatos:
        score = len(tokens_sofa & normalizar_nome(jogador.nome))
        if score > melhor_score:
            melhor_score = score
            melhor = jogador
    return melhor if melhor_score > 0 else None


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
            mudou = False
            for campo_sofa, campo_nosso in MAPA_CAMPOS.items():
                if getattr(linha, campo_nosso) is None and campo_sofa in stats_sofa:
                    setattr(linha, campo_nosso, stats_sofa[campo_sofa])
                    mudou = True
            if mudou:
                atualizadas += 1

    db.commit()
    return atualizadas


def enriquecer_rodada(rodada):
    db = SessionLocal()
    try:
        partidas = (
            db.query(Partida)
            .filter(Partida.campeonato_id == 1, Partida.rodada == rodada, Partida.status == "finalizada")
            .all()
        )
        if not partidas:
            print(f"Nenhuma partida finalizada encontrada pra rodada {rodada}.")
            return

        eventos_rodada = buscar_eventos_rodada(rodada)
        print(f"{len(eventos_rodada)} eventos do SofaScore encontrados pra rodada {rodada}.")

        for partida in partidas:
            evento = encontrar_evento(partida, eventos_rodada)
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
    if len(sys.argv) != 2:
        print("Uso: py scripts/enriquecer_sofascore.py <numero_da_rodada>")
        sys.exit(1)
    enriquecer_rodada(int(sys.argv[1]))
