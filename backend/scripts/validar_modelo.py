from app.database import SessionLocal
from app.models.time import Time
from app.models.partida import Partida
from app.services.gols_esperados import calcular_gols_esperados
from app.services.probabilidade_resultado import calcular_probabilidade_resultado
from app.services.escanteios_esperados import calcular_escanteios_esperados
from app.services.cartoes_esperados import calcular_cartoes_esperados


def resultado_real(gols_mandante, gols_visitante):
    if gols_mandante > gols_visitante:
        return "mandante"
    if gols_mandante < gols_visitante:
        return "visitante"
    return "empate"


def resultado_previsto(prob):
    maior = max(
        ("mandante", prob["probabilidade_vitoria_mandante"]),
        ("empate", prob["probabilidade_empate"]),
        ("visitante", prob["probabilidade_vitoria_visitante"]),
        key=lambda par: par[1],
    )
    return maior[0]


def validar():
    db = SessionLocal()

    jogos_reais = (
        db.query(Partida)
        .filter(Partida.id_externo.isnot(None))
        .order_by(Partida.data.asc())
        .all()
    )

    print(f"{len(jogos_reais)} jogos reais encontrados no banco.\n")

    validados = 0
    pulados = 0

    erros_gols = []
    erros_escanteios = []
    erros_cartoes = []
    acertos_resultado = 0

    for jogo in jogos_reais:
        data_referencia = jogo.data

        gols = calcular_gols_esperados(db, jogo.time_mandante_id, jogo.time_visitante_id, data_referencia)
        if gols.get("gols_esperados_mandante") is None:
            pulados += 1
            continue

        prob = calcular_probabilidade_resultado(db, jogo.time_mandante_id, jogo.time_visitante_id, data_referencia)
        escanteios = calcular_escanteios_esperados(db, jogo.time_mandante_id, jogo.time_visitante_id, data_referencia)
        cartoes = calcular_cartoes_esperados(db, jogo.time_mandante_id, jogo.time_visitante_id, data_referencia)

        if prob.get("probabilidade_vitoria_mandante") is None:
            pulados += 1
            continue

        validados += 1

        # erro de gols (média do erro absoluto dos dois lados)
        erro_gols_mandante = abs(gols["gols_esperados_mandante"] - jogo.gols_mandante)
        erro_gols_visitante = abs(gols["gols_esperados_visitante"] - jogo.gols_visitante)
        erros_gols.append((erro_gols_mandante + erro_gols_visitante) / 2)

        # acerto de resultado
        real = resultado_real(jogo.gols_mandante, jogo.gols_visitante)
        previsto = resultado_previsto(prob)
        acerto = real == previsto
        if acerto:
            acertos_resultado += 1

        # erro de escanteios (total)
        if escanteios.get("total_esperado") is not None:
            total_real_escanteios = jogo.escanteios_mandante + jogo.escanteios_visitante
            erros_escanteios.append(abs(escanteios["total_esperado"] - total_real_escanteios))

        # erro de cartões (total, amarelos + vermelhos)
        if cartoes.get("total_cartoes_esperado") is not None:
            total_real_cartoes = (
                jogo.cartoes_amarelos_mandante + jogo.cartoes_amarelos_visitante
                + jogo.cartoes_vermelhos_mandante + jogo.cartoes_vermelhos_visitante
            )
            erros_cartoes.append(abs(cartoes["total_cartoes_esperado"] - total_real_cartoes))

        time_mandante = db.query(Time).filter(Time.id == jogo.time_mandante_id).first()
        time_visitante = db.query(Time).filter(Time.id == jogo.time_visitante_id).first()

        print(f"  {jogo.data} | {time_mandante.nome} {jogo.gols_mandante} x {jogo.gols_visitante} "
              f"{time_visitante.nome} | previsto: {gols['gols_esperados_mandante']} x "
              f"{gols['gols_esperados_visitante']} | resultado real: {real}, previsto: {previsto} "
              f"({'ACERTOU' if acerto else 'errou'})")

    print(f"\n{'=' * 60}")
    print(f"Validação concluída: {validados} jogos validados, {pulados} pulados (histórico insuficiente).\n")

    if validados > 0:
        print(f"Erro médio absoluto de gols: {round(sum(erros_gols) / len(erros_gols), 2)}")
        print(f"Acerto de resultado (V/E/D): {round((acertos_resultado / validados) * 100, 1)}% "
              f"({acertos_resultado}/{validados})")
        if erros_escanteios:
            print(f"Erro médio absoluto de escanteios (total): {round(sum(erros_escanteios) / len(erros_escanteios), 2)}")
        if erros_cartoes:
            print(f"Erro médio absoluto de cartões (total): {round(sum(erros_cartoes) / len(erros_cartoes), 2)}")

    db.close()


if __name__ == "__main__":
    validar()