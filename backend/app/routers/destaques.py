from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.partida import Partida
from app.schemas.destaque import Destaque, DestaqueJogador, JogoComDestaques, DestaquesRodadaResponse
from app.services.destaques import calcular_destaques_time, calcular_destaques_jogadores_time

router = APIRouter(prefix="/destaques", tags=["Destaques"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/rodada/{numero}", response_model=DestaquesRodadaResponse)
def obter_destaques_rodada(numero: int, db: Session = Depends(get_db)):
    """
    Pra cada confronto ainda nao jogado da rodada, acha sequencias que
    chamam atencao no historico recente de cada time (no mando de campo
    que ele vai ter nesse jogo). So retorna jogos com pelo menos um
    destaque -- rodada sem nada notavel vem com "jogos": [].
    """
    partidas = (
        db.query(Partida)
        .filter(Partida.rodada == numero, Partida.status == "agendada")
        .order_by(Partida.data.is_(None), Partida.data)
        .all()
    )

    if not partidas:
        raise HTTPException(
            status_code=404, detail="Nenhum confronto agendado encontrado para essa rodada"
        )

    jogos = []
    for p in partidas:
        data_referencia = p.data or date.today()

        destaques_mandante = calcular_destaques_time(db, p.time_mandante_id, "mandante", data_referencia)
        destaques_visitante = calcular_destaques_time(db, p.time_visitante_id, "visitante", data_referencia)
        destaques_jogadores_mandante = calcular_destaques_jogadores_time(db, p.time_mandante_id)
        destaques_jogadores_visitante = calcular_destaques_jogadores_time(db, p.time_visitante_id)

        if not any(
            [destaques_mandante, destaques_visitante, destaques_jogadores_mandante, destaques_jogadores_visitante]
        ):
            continue

        jogos.append(
            JogoComDestaques(
                partida_id=p.id,
                data=str(p.data) if p.data else None,
                rodada=numero,
                time_mandante_id=p.time_mandante_id,
                time_mandante=p.time_mandante.nome,
                time_visitante_id=p.time_visitante_id,
                time_visitante=p.time_visitante.nome,
                destaques_mandante=[Destaque(**d) for d in destaques_mandante],
                destaques_visitante=[Destaque(**d) for d in destaques_visitante],
                destaques_jogadores_mandante=[DestaqueJogador(**j) for j in destaques_jogadores_mandante],
                destaques_jogadores_visitante=[DestaqueJogador(**j) for j in destaques_jogadores_visitante],
            )
        )

    return DestaquesRodadaResponse(rodada=numero, jogos=jogos)
