# -*- coding: utf-8 -*-
"""
Renomeia Jogador.posicao de "Zagueiro" pra "Defensor" -- Vitor pediu um
rotulo mais generico (cobre lateral/zagueiro/ala, nao so' zagueiro
central). Idempotente: so' atualiza quem ainda estiver com o valor
antigo, seguro rodar de novo.

Uso (de dentro de backend/; local usa SQLite, ver
migrar_posicao_defensor_producao.py pra producao):
    py scripts/migrar_posicao_defensor.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.time import Time  # noqa: F401 -- precisa estar registrado pro relationship de Jogador resolver
from app.models.jogador import Jogador


def migrar():
    db = SessionLocal()
    try:
        atualizados = db.query(Jogador).filter(Jogador.posicao == "Zagueiro").update({"posicao": "Defensor"})
        db.commit()
        print(f"{atualizados} jogador(es) atualizado(s) de 'Zagueiro' pra 'Defensor'.")
    finally:
        db.close()


if __name__ == "__main__":
    migrar()
