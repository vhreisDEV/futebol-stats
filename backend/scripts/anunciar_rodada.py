# -*- coding: utf-8 -*-
"""
Monta e manda o aviso de rodada nova pro bot do Telegram, puxando um
destaque de verdade (o bilhete de maior confianca entre os jogos da
rodada) em vez de um texto generico -- reaproveita o cache ja calculado
em AnaliseIAPartida.destaques_json (ver app/routers/analise_ia.py), sem
recalcular nada nem gastar cota da Highlightly.

Uso (de dentro de backend/; local usa SQLite, ver
anunciar_rodada_producao.py pra producao):
    py scripts/anunciar_rodada.py 25
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:  # console do Windows costuma usar cp1252, que quebra nos emojis do print
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

from app.database import SessionLocal
from app.models.time import Time  # noqa: F401 -- precisa estar importado pro relationship de Partida resolver
from app.models.partida import Partida
from app.models.analise_ia import AnaliseIAPartida
from app.services.telegram import enviar_broadcast, BotNaoConfiguradoError

URL_SITE = "https://veaga-psi.vercel.app"


DIAS_SEMANA = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]


def _data_formatada(partida):
    if not partida.data:
        return ""
    dia_semana = DIAS_SEMANA[partida.data.weekday()]
    texto = f"{dia_semana}, {partida.data.strftime('%d/%m')}"
    if partida.hora:
        texto += f" às {partida.hora.strftime('%Hh%M')}"
    return texto


def _frase_perna(perna):
    mando = "em casa" if perna["time"] == "mandante" else "fora de casa"
    d = perna["destaque"]
    nome = perna["nome_time"]
    if d["tipo"] == "booleano":
        return f"{nome} {mando}: {d['label'].lower()}"
    return f"{nome} {mando} tende a passar de {d['linha']} {d['label'].lower()}"


def montar_mensagem_rodada(db, campeonato_id, numero_rodada):
    partidas = (
        db.query(Partida)
        .filter(
            Partida.campeonato_id == campeonato_id,
            Partida.rodada == numero_rodada,
            Partida.status == "agendada",
        )
        .all()
    )
    if not partidas:
        return None

    melhor = None  # (confianca, partida, perna)
    for p in partidas:
        cache = db.query(AnaliseIAPartida).filter_by(partida_id=p.id).first()
        if not cache or not cache.destaques_json:
            continue
        bilhete_simples = json.loads(cache.destaques_json).get("bilhete_simples")
        if not bilhete_simples:
            continue
        confianca = bilhete_simples["confianca"]
        if melhor is None or confianca > melhor[0]:
            melhor = (confianca, p, bilhete_simples["perna"])

    # Cada bloco e' separado por linha em branco (join com "\n\n") --
    # dentro do bloco de destaque, cada informacao (titulo, confronto,
    # palpite) fica na propria linha, pra nao ficar tudo amontoado numa
    # frase so.
    blocos = [f"Fala, {{nome}}! A Rodada {numero_rodada} do Brasileirão já tem <b>Análise IA</b> no ar."]

    if melhor:
        _, partida_destaque, perna = melhor
        acertos = perna["destaque"]["acertos"]
        total = perna["destaque"]["total"]
        quando = _data_formatada(partida_destaque)

        confronto = f"{partida_destaque.time_mandante.nome} x {partida_destaque.time_visitante.nome}"
        if quando:
            confronto += f" — {quando}"

        blocos.append(
            "🔥 <b>Melhor palpite da rodada</b>\n\n"
            f"📅 {confronto}\n"
            f"🎯 {_frase_perna(perna)} (acertou em {acertos} de {total} jogos)"
        )
        link_id = partida_destaque.id
        restantes = len(partidas) - 1
    else:
        link_id = partidas[0].id
        restantes = len(partidas)

    if restantes > 0:
        plural = "jogo" if restantes == 1 else "jogos"
        blocos.append(f"📊 Mais {restantes} {plural} com Análise IA disponível nesta rodada.")

    blocos.append(f"👉 Dá uma olhada: {URL_SITE}/analise/{link_id}")

    return "\n\n".join(blocos)


def anunciar_rodada(campeonato_id, numero_rodada, dry_run=False):
    db = SessionLocal()
    try:
        texto = montar_mensagem_rodada(db, campeonato_id, numero_rodada)
        if texto is None:
            print(f"Nenhuma partida agendada encontrada pra rodada {numero_rodada}.")
            return

        print("--- Preview ---")
        print(texto.replace("{nome}", "torcedor"))
        print("---")

        if dry_run:
            print("Modo --dry-run: nada foi enviado.")
            return

        try:
            enviados, desativados = enviar_broadcast(db, texto)
            print(f"Mensagem enviada pra {enviados} inscrito(s). {desativados} marcado(s) como inativo.")
        except BotNaoConfiguradoError:
            print("ERRO: TELEGRAM_BOT_TOKEN não encontrada no .env")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: py scripts/anunciar_rodada.py <numero_da_rodada> [--dry-run]")
        sys.exit(1)
    anunciar_rodada(campeonato_id=1, numero_rodada=int(sys.argv[1]), dry_run="--dry-run" in sys.argv)
