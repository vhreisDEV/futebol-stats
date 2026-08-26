import os

import requests

from app.models.telegram_subscriber import TelegramSubscriber

BASE_URL = "https://api.telegram.org"


class BotNaoConfiguradoError(Exception):
    pass


def _token():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise BotNaoConfiguradoError()
    return token


def enviar_mensagem(chat_id, texto):
    """Manda uma mensagem pra um chat especifico. Devolve True se o
    Telegram aceitou, False se falhou (ex.: usuario bloqueou o bot --
    quem chama decide se marca o inscrito como inativo)."""
    resp = requests.post(
        f"{BASE_URL}/bot{_token()}/sendMessage",
        # disable_web_page_preview=True -- o site nao tem Open Graph
        # configurado ainda, entao o card de preview do link saia feio/
        # vazio. Sem isso, so o texto mesmo (o link continua clicavel).
        json={"chat_id": chat_id, "text": texto, "parse_mode": "HTML", "disable_web_page_preview": True},
        timeout=10,
    )
    return resp.ok


def registrar_inscrito(db, chat_id, nome=None):
    inscrito = db.query(TelegramSubscriber).filter(TelegramSubscriber.chat_id == chat_id).first()
    if inscrito:
        inscrito.ativo = True
        if nome:
            inscrito.nome = nome
    else:
        inscrito = TelegramSubscriber(chat_id=chat_id, nome=nome, ativo=True)
        db.add(inscrito)
    db.commit()
    return inscrito


def cancelar_inscrito(db, chat_id):
    inscrito = db.query(TelegramSubscriber).filter(TelegramSubscriber.chat_id == chat_id).first()
    if inscrito:
        inscrito.ativo = False
        db.commit()


def enviar_broadcast(db, texto):
    """Manda a mesma mensagem pra todo inscrito ativo. Se o texto tiver
    "{nome}", cada um recebe com o proprio primeiro nome no lugar (cai
    pra "torcedor" em quem se inscreveu antes de guardarmos o nome).
    Quem apanhar um 403 (usuario bloqueou o bot) e' marcado como
    inativo na hora, pra nao tentar de novo no proximo broadcast.
    Devolve (enviados, desativados)."""
    inscritos = db.query(TelegramSubscriber).filter(TelegramSubscriber.ativo.is_(True)).all()
    enviados = 0
    desativados = 0
    for inscrito in inscritos:
        texto_pessoal = texto.replace("{nome}", inscrito.nome or "torcedor")
        resp = requests.post(
            f"{BASE_URL}/bot{_token()}/sendMessage",
            json={
                "chat_id": inscrito.chat_id,
                "text": texto_pessoal,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
            timeout=10,
        )
        if resp.ok:
            enviados += 1
        elif resp.status_code == 403:
            inscrito.ativo = False
            desativados += 1
    db.commit()
    return enviados, desativados
