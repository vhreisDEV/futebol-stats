# -*- coding: utf-8 -*-
"""
Manda uma mensagem de broadcast pra todo inscrito ativo do bot do
Telegram. Uso tipico: avisar que a Dica da Rodada / Analise IA de uma
nova rodada ja esta disponivel.

Uso (de dentro de backend/; local usa SQLite, ver
notificar_telegram_producao.py pra producao):
    py scripts/notificar_telegram.py "Rodada 25 liberada! Dicas e Analise IA ja estao no ar. https://veaga-psi.vercel.app"
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.services.telegram import enviar_broadcast, BotNaoConfiguradoError


def notificar(texto):
    db = SessionLocal()
    try:
        enviados, desativados = enviar_broadcast(db, texto)
        print(f"Mensagem enviada pra {enviados} inscrito(s). {desativados} marcado(s) como inativo (bot bloqueado).")
    except BotNaoConfiguradoError:
        print("ERRO: TELEGRAM_BOT_TOKEN não encontrada no .env")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Uso: py scripts/notificar_telegram.py "texto da mensagem"')
        sys.exit(1)
    notificar(sys.argv[1])
