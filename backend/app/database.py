import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

# Producao (Render) injeta DATABASE_URL apontando pro Postgres. Sem essa
# variavel (dev local, os dois computadores do Victor), continua usando o
# arquivo SQLite de sempre -- nada muda no fluxo local.
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./futebol_stats.db")

# Render (como a maioria dos hosts de Postgres) as vezes ainda entrega a URL
# com o prefixo antigo "postgres://", que o SQLAlchemy 2.x nao aceita mais.
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
