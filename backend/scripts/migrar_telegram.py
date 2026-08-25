"""
Cria a tabela `telegram_subscribers` (inscritos do bot de notificacao do
VEAGA no Telegram). So roda uma vez.

Uso (de dentro de backend/):
    py scripts/migrar_telegram.py
"""
from app.database import Base, engine
from app.models.telegram_subscriber import TelegramSubscriber


def migrar():
    Base.metadata.create_all(bind=engine, tables=[TelegramSubscriber.__table__])
    print("Tabela 'telegram_subscribers' garantida (criada se ainda nao existia).")


if __name__ == "__main__":
    migrar()
