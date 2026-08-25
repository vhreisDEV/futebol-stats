# -*- coding: utf-8 -*-
"""
Registra a URL de webhook do backend no Telegram (chamada UNICA, so
precisa rodar de novo se o token do bot ou a URL do backend mudar).
Precisa de TELEGRAM_BOT_TOKEN (e, se quiser, TELEGRAM_WEBHOOK_SECRET)
no .env.

Uso (de dentro de backend/):
    py scripts/registrar_webhook_telegram.py https://veaga-backend.onrender.com
"""
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SEGREDO = os.getenv("TELEGRAM_WEBHOOK_SECRET")


def registrar(base_url):
    if not TOKEN:
        print("ERRO: TELEGRAM_BOT_TOKEN não encontrada no .env")
        return

    payload = {"url": f"{base_url.rstrip('/')}/telegram/webhook"}
    if SEGREDO:
        payload["secret_token"] = SEGREDO

    resp = requests.post(f"https://api.telegram.org/bot{TOKEN}/setWebhook", json=payload, timeout=10)
    print(resp.status_code, resp.json())


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: py scripts/registrar_webhook_telegram.py <url-base-do-backend>")
        sys.exit(1)
    registrar(sys.argv[1])
