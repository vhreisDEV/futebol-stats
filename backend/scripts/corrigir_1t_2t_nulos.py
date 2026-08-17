from app.database import SessionLocal
from app.models.time import Time  # noqa: F401 -- precisa estar importado para o relationship("Time") resolver
from app.models.partida import Partida

# O modelo Partida tinha "default=0" nos campos de 1o/2o tempo de
# escanteios e chutes, mesmo eles sendo nullable=True. O SQLAlchemy
# aplica esse default mesmo quando o codigo de importacao passa
# explicitamente None, entao toda partida real ficou gravada com 0
# nesses campos em vez de nulo (a Highlightly nao fornece esse dado
# granular). Esse script corrige os dados ja salvos; o default=0 foi
# removido do modelo, entao importacoes futuras ja gravam nulo certo.

CAMPOS = [
    "escanteios_1t_mandante",
    "escanteios_1t_visitante",
    "escanteios_2t_mandante",
    "escanteios_2t_visitante",
    "chutes_1t_mandante",
    "chutes_1t_visitante",
]


def corrigir():
    db = SessionLocal()

    try:
        partidas = db.query(Partida).all()
        corrigidas = 0

        for partida in partidas:
            mudou = False
            for campo in CAMPOS:
                if getattr(partida, campo) == 0:
                    setattr(partida, campo, None)
                    mudou = True
            if mudou:
                corrigidas += 1

        db.commit()
        print(f"{corrigidas} de {len(partidas)} partidas corrigidas (campos de 1T/2T zerados -> nulo).")

    finally:
        db.close()


if __name__ == "__main__":
    corrigir()
