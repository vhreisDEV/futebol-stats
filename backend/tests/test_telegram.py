"""Testa a logica de inscricao/cancelamento do bot do Telegram contra um
SQLite isolado em memoria -- nao faz nenhuma chamada real a API do
Telegram (enviar_mensagem/enviar_broadcast ficam de fora de proposito)."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.telegram_subscriber import TelegramSubscriber
from app.services.telegram import registrar_inscrito, cancelar_inscrito


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine, tables=[TelegramSubscriber.__table__])
    Sessao = sessionmaker(bind=engine)
    sessao = Sessao()
    yield sessao
    sessao.close()


def test_registrar_inscrito_novo(db):
    registrar_inscrito(db, chat_id=123)

    inscrito = db.query(TelegramSubscriber).filter_by(chat_id=123).first()
    assert inscrito is not None
    assert inscrito.ativo is True


def test_registrar_inscrito_ja_existente_nao_duplica(db):
    registrar_inscrito(db, chat_id=123)
    registrar_inscrito(db, chat_id=123)

    total = db.query(TelegramSubscriber).filter_by(chat_id=123).count()
    assert total == 1


def test_cancelar_inscrito_marca_inativo_sem_deletar(db):
    registrar_inscrito(db, chat_id=123)
    cancelar_inscrito(db, chat_id=123)

    inscrito = db.query(TelegramSubscriber).filter_by(chat_id=123).first()
    assert inscrito is not None
    assert inscrito.ativo is False


def test_dar_start_de_novo_depois_de_parar_reativa(db):
    registrar_inscrito(db, chat_id=123)
    cancelar_inscrito(db, chat_id=123)
    registrar_inscrito(db, chat_id=123)

    inscrito = db.query(TelegramSubscriber).filter_by(chat_id=123).first()
    assert inscrito.ativo is True


def test_cancelar_inscrito_inexistente_nao_quebra(db):
    cancelar_inscrito(db, chat_id=999)  # nunca deu /start -- so' nao deve levantar excecao
    assert db.query(TelegramSubscriber).count() == 0
