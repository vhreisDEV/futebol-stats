"""Testa a logica de inscricao/cancelamento do bot do Telegram contra um
SQLite isolado em memoria -- nao faz nenhuma chamada real a API do
Telegram (as chamadas de envio sao mockadas onde precisam ser
exercitadas, ex.: personalizacao do broadcast)."""
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import BigInteger, create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.telegram_subscriber import TelegramSubscriber
from app.services.telegram import registrar_inscrito, cancelar_inscrito, enviar_broadcast


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


def test_chat_id_e_bigint():
    # Regressao real: um chat_id do Telegram maior que 2.147.483.647 (o
    # limite de um Integer comum) causava overflow no Postgres de
    # producao -- silencioso no SQLite local, que nao reforca largura de
    # coluna, por isso so apareceu com um usuario real testando o bot.
    assert isinstance(TelegramSubscriber.chat_id.type, BigInteger)


def test_registrar_inscrito_com_chat_id_maior_que_int32(db):
    chat_id_grande = 5123456789  # > 2.147.483.647
    registrar_inscrito(db, chat_id=chat_id_grande)

    inscrito = db.query(TelegramSubscriber).filter_by(chat_id=chat_id_grande).first()
    assert inscrito is not None
    assert inscrito.chat_id == chat_id_grande


def test_registrar_inscrito_guarda_nome(db):
    registrar_inscrito(db, chat_id=123, nome="Victor")

    inscrito = db.query(TelegramSubscriber).filter_by(chat_id=123).first()
    assert inscrito.nome == "Victor"


def test_dar_start_de_novo_atualiza_nome(db):
    registrar_inscrito(db, chat_id=123, nome="Victor")
    registrar_inscrito(db, chat_id=123, nome="Victor Hugo")

    inscrito = db.query(TelegramSubscriber).filter_by(chat_id=123).first()
    assert inscrito.nome == "Victor Hugo"


def test_broadcast_personaliza_com_o_nome_de_cada_inscrito(db):
    registrar_inscrito(db, chat_id=111, nome="Ana")
    registrar_inscrito(db, chat_id=222, nome=None)  # inscrito antigo, sem nome guardado

    with patch("app.services.telegram.os.getenv", return_value="token-fake"), patch(
        "app.services.telegram.requests.post"
    ) as mock_post:
        mock_post.return_value = MagicMock(ok=True, status_code=200)
        enviar_broadcast(db, "Fala, {nome}! Saiu a rodada nova.")

    textos_enviados = [chamada.kwargs["json"]["text"] for chamada in mock_post.call_args_list]
    assert "Fala, Ana! Saiu a rodada nova." in textos_enviados
    assert "Fala, torcedor! Saiu a rodada nova." in textos_enviados
