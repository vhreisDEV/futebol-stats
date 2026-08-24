from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from app.database import Base

class Time(Base):
    __tablename__ = "times"
    __table_args__ = (
        # Unico por campeonato, nao globalmente -- dois campeonatos
        # diferentes podem, em tese, ter um time com o mesmo nome.
        UniqueConstraint("nome", "campeonato_id", name="uq_time_nome_campeonato"),
    )

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True, nullable=False)
    id_externo = Column(Integer, unique=True, nullable=True, index=True)
    # Nullable por enquanto: times ja existentes (todos do Brasileirao) sao
    # backfilled na migracao logo depois de criar essa coluna.
    campeonato_id = Column(Integer, ForeignKey("campeonatos.id"), nullable=True, index=True)