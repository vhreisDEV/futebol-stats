"""
Cria a tabela `analises_ia_partida` (cache da analise gerada por IA por
partida -- gerar uma vez, nunca de novo, pra nao gastar chamada de API
toda vez que alguem abre a pagina). So roda uma vez.

Uso (de dentro de backend/):
    py scripts/migrar_analise_ia.py
"""
from app.database import Base, engine
from app.models.partida import Partida  # noqa: F401 -- precisa estar importado pro ForeignKey resolver
from app.models.analise_ia import AnaliseIAPartida


def migrar():
    Base.metadata.create_all(bind=engine, tables=[AnaliseIAPartida.__table__])
    print("Tabela 'analises_ia_partida' garantida (criada se ainda nao existia).")


if __name__ == "__main__":
    migrar()
