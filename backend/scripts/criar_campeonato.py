"""
Cria (ou confirma que ja existe) uma linha de Campeonato -- passo 0 antes
de sincronizar times/importar partidas de uma liga nova. Idempotente:
identifica o campeonato existente por id_externo_liga, nunca duplica.

Uso (de dentro de backend/, edite CAMPEONATOS_CONHECIDOS ou chame
criar_campeonato(...) direto):
    py scripts/criar_campeonato.py <id_externo_liga>
"""
import sys

from app.database import SessionLocal
from app.models.campeonato import Campeonato

# IDs de liga na Highlightly confirmados em 2026-08-24 (temporada 2026 =
# 26/27 para as ligas europeias). rodadas_total assume 38 (20 times,
# turno+returno) -- ligas com numero diferente de times precisam de outro
# valor (ex.: Bundesliga com 18 times tem 34 rodadas).
#
# temporada_dupla=True: rotulo vira "2026-27" (temporada europeia,
# atravessa dois anos civis). False: rotulo e' so o ano ("2026", caso do
# Brasileirao e outras ligas de calendario unico).
CAMPEONATOS_CONHECIDOS = {
    33973: dict(nome="Premier League", pais_nome="Inglaterra", pais_codigo="GB-ENG", rodadas_total=38, temporada_dupla=True),
    119924: dict(nome="La Liga", pais_nome="Espanha", pais_codigo="ES", rodadas_total=38, temporada_dupla=True),
    67162: dict(nome="Bundesliga", pais_nome="Alemanha", pais_codigo="DE", rodadas_total=34, temporada_dupla=True),
    115669: dict(nome="Serie A", pais_nome="Itália", pais_codigo="IT", rodadas_total=38, temporada_dupla=True),
    52695: dict(nome="Ligue 1", pais_nome="França", pais_codigo="FR", rodadas_total=34, temporada_dupla=True),
}


def montar_temporada_label(temporada, temporada_dupla):
    if temporada_dupla:
        return f"{temporada}-{str(temporada + 1)[-2:]}"
    return str(temporada)


def criar_campeonato(db, id_externo_liga, temporada=2026):
    existente = db.query(Campeonato).filter(Campeonato.id_externo_liga == id_externo_liga).first()
    if existente:
        print(f"Ja existia: {existente.nome} (id={existente.id}).")
        return existente

    info = CAMPEONATOS_CONHECIDOS.get(id_externo_liga)
    if not info:
        raise ValueError(
            f"id_externo_liga={id_externo_liga} nao esta em CAMPEONATOS_CONHECIDOS -- adicione antes de rodar."
        )

    campeonato = Campeonato(
        nome=info["nome"],
        pais_nome=info["pais_nome"],
        pais_codigo=info["pais_codigo"],
        temporada=temporada,
        temporada_label=montar_temporada_label(temporada, info["temporada_dupla"]),
        id_externo_liga=id_externo_liga,
        rodadas_total=info["rodadas_total"],
        ativo=True,
    )
    db.add(campeonato)
    db.commit()
    db.refresh(campeonato)
    print(f"Criado: {campeonato.nome} (id={campeonato.id}).")
    return campeonato


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: py scripts/criar_campeonato.py <id_externo_liga>")
        sys.exit(1)

    db = SessionLocal()
    try:
        criar_campeonato(db, int(sys.argv[1]))
    finally:
        db.close()
