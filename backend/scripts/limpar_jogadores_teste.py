"""Apaga todos os Jogador/EstatisticaJogadorPartida (dado ficticio de teste),
sem tocar em Time/Partida. Rode antes de gerar de novo ou antes de importar
dados reais de jogador."""

from app.database import SessionLocal
from app.models.jogador import Jogador
from app.models.estatistica_jogador_partida import EstatisticaJogadorPartida


def limpar():
    db = SessionLocal()
    try:
        linhas = db.query(EstatisticaJogadorPartida).delete()
        jogadores = db.query(Jogador).delete()
        db.commit()
        print(f"Apagado: {jogadores} jogadores, {linhas} linhas de estatistica.")
    finally:
        db.close()


if __name__ == "__main__":
    limpar()
