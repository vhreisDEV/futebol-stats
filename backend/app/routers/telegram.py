import os
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.services.telegram import enviar_mensagem, registrar_inscrito, cancelar_inscrito, BotNaoConfiguradoError

router = APIRouter(prefix="/telegram", tags=["Telegram"])

def montar_mensagem_boas_vindas(nome):
    saudacao = f"Fala, {nome}! 👋" if nome else "Fala! 👋"
    return (
        f"{saudacao} Bem-vindo à <b>Súmula do VEAGA</b> ⚽📋\n\n"
        "A partir de agora você recebe aqui, em primeira mão, o aviso sempre que "
        "uma rodada nova estiver com <b>Análise IA</b> e <b>Dicas da Rodada</b> no ar.\n\n"
        "Pra parar de receber, é só mandar /parar quando quiser."
    )


MENSAGEM_CANCELAMENTO = "Inscrição cancelada. Você pode voltar quando quiser com /start. 👋"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/webhook")
def webhook(
    update: dict,
    db: Session = Depends(get_db),
    x_telegram_bot_api_secret_token: Optional[str] = Header(None),
):
    # Telegram manda esse header exatamente igual ao secret_token passado
    # no setWebhook -- confere pra ninguem conseguir forjar update (ex.:
    # registrar chat_id arbitrario) so' fazendo POST direto na rota.
    segredo_esperado = os.getenv("TELEGRAM_WEBHOOK_SECRET")
    if segredo_esperado and x_telegram_bot_api_secret_token != segredo_esperado:
        raise HTTPException(status_code=403, detail="Token de webhook invalido")

    mensagem = update.get("message")
    if not mensagem:
        return {"ok": True}

    chat_id = mensagem.get("chat", {}).get("id")
    texto = (mensagem.get("text") or "").strip().lower()
    nome = mensagem.get("from", {}).get("first_name")
    if chat_id is None:
        return {"ok": True}

    try:
        if texto in ("/start", "/start@veaga_dicas_bot"):
            registrar_inscrito(db, chat_id, nome=nome)
            enviar_mensagem(chat_id, montar_mensagem_boas_vindas(nome))
        elif texto in ("/parar", "/stop"):
            cancelar_inscrito(db, chat_id)
            enviar_mensagem(chat_id, MENSAGEM_CANCELAMENTO)
    except BotNaoConfiguradoError:
        pass

    return {"ok": True}
