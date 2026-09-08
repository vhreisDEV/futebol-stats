from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.campeonato import Campeonato
from app.models.partida import Partida
from app.models.time import Time
from app.schemas.campeonato import CampeonatoResponse, ListaCampeonatosResponse

router = APIRouter(prefix="/campeonatos", tags=["Campeonatos"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _jogos_minimo_por_time(db, campeonato_id):
    # MAX(rodada) sozinho engana quando uma partida e' remarcada pra uma
    # rodada futura (ex.: La Liga rodada 6 com so' 1 jogo, o resto dos
    # times ainda na rodada 4) -- isso faria a liga inteira parecer mais
    # adiantada do que realmente esta. Conta jogo a jogo por time e pega
    # o time que jogou MENOS vezes, que e' o dado que realmente importa
    # pra saber se da pra confiar numa media de "ultimos N jogos".
    times_ids = [time_id for (time_id,) in db.query(Time.id).filter(Time.campeonato_id == campeonato_id).all()]
    if not times_ids:
        return None

    contagem = {time_id: 0 for time_id in times_ids}
    finalizadas = (
        db.query(Partida.time_mandante_id, Partida.time_visitante_id)
        .filter(Partida.campeonato_id == campeonato_id, Partida.status == "finalizada")
        .all()
    )
    for mandante_id, visitante_id in finalizadas:
        if mandante_id in contagem:
            contagem[mandante_id] += 1
        if visitante_id in contagem:
            contagem[visitante_id] += 1

    return min(contagem.values())


def _montar_response(db, c):
    rodada_atual = (
        db.query(func.max(Partida.rodada))
        .filter(Partida.campeonato_id == c.id, Partida.status == "finalizada")
        .scalar()
    )
    total_times = db.query(Time).filter(Time.campeonato_id == c.id).count()
    jogos_minimo_time = _jogos_minimo_por_time(db, c.id)

    return CampeonatoResponse(
        id=c.id,
        nome=c.nome,
        pais_nome=c.pais_nome,
        pais_codigo=c.pais_codigo,
        temporada=c.temporada,
        temporada_label=c.temporada_label,
        rodadas_total=c.rodadas_total,
        ativo=c.ativo,
        rodada_atual=rodada_atual,
        total_times=total_times,
        jogos_minimo_time=jogos_minimo_time,
    )


@router.get("/", response_model=ListaCampeonatosResponse)
def listar_campeonatos(db: Session = Depends(get_db)):
    campeonatos = db.query(Campeonato).filter(Campeonato.ativo.is_(True)).order_by(Campeonato.id).all()
    return ListaCampeonatosResponse(campeonatos=[_montar_response(db, c) for c in campeonatos])


@router.get("/{campeonato_id}", response_model=CampeonatoResponse)
def obter_campeonato(campeonato_id: int, db: Session = Depends(get_db)):
    campeonato = db.query(Campeonato).filter(Campeonato.id == campeonato_id).first()
    if not campeonato:
        raise HTTPException(status_code=404, detail="Campeonato nao encontrado")
    return _montar_response(db, campeonato)
