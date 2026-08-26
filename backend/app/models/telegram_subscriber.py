from sqlalchemy import Column, Integer, BigInteger, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class TelegramSubscriber(Base):
    __tablename__ = "telegram_subscribers"

    id = Column(Integer, primary_key=True, index=True)
    # Identificador do chat no Telegram -- unico por usuario/grupo que deu
    # /start no bot. E' o unico dado que precisamos guardar (o bot nao
    # tem conceito de conta VEAGA nenhuma, so avisa quem deu /start).
    # BigInteger e' obrigatorio aqui: contas novas do Telegram ja tem id
    # maior que o limite de um Integer normal (2.147.483.647) -- um
    # Integer comum causava overflow no Postgres de producao (silencioso
    # no SQLite local, que nao reforca o tamanho do campo, por isso so
    # apareceu com um chat_id real).
    chat_id = Column(BigInteger, unique=True, nullable=False, index=True)
    # False quando o usuario deu /parar (ou bloqueou o bot e o envio
    # devolveu 403) -- nunca deletamos a linha, so paramos de mandar.
    ativo = Column(Boolean, nullable=False, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
