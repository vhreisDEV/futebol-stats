"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Time {
  id: number;
  nome: string;
}

interface Projecao {
  time_mandante: string;
  time_visitante: string;
  data_referencia: string;
  gols: {
    mandante: number | null;
    visitante: number | null;
  };
  resultado: {
    vitoria_mandante: number | null;
    empate: number | null;
    vitoria_visitante: number | null;
  };
  escanteios: {
    mandante: number | null;
    visitante: number | null;
    total: number | null;
    linha_referencia: number | null;
    tendencia: string | null;
  };
  cartoes: {
    amarelos_mandante: number | null;
    amarelos_visitante: number | null;
    vermelhos_mandante: number | null;
    vermelhos_visitante: number | null;
    total: number | null;
    linha_referencia: number | null;
    tendencia: string | null;
  };
  chutes: {
    totais_mandante: number | null;
    totais_visitante: number | null;
    ao_gol_mandante: number | null;
    ao_gol_visitante: number | null;
    primeiro_tempo_mandante: number | null;
    primeiro_tempo_visitante: number | null;
  };
}

function valorOuTraco(valor: number | null) {
  return valor === null || valor === undefined ? "—" : valor;
}

function placarArredondado(valor: number | null) {
  return valor === null || valor === undefined ? "—" : Math.round(valor);
}

function corDoFavorito(valor: number | null, outros: (number | null)[]) {
  if (valor === null) return "text-muted-foreground";
  const eMaior = outros.every((outro) => outro === null || valor >= outro);
  return eMaior ? "text-primary" : "text-muted-foreground";
}

function CartaoProjecao({ titulo, children }: { titulo: string; children: React.ReactNode }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-xs uppercase tracking-wide text-muted-foreground">
          {titulo}
        </CardTitle>
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}

function LinhaComparativa({
  label,
  valorMandante,
  valorVisitante,
}: {
  label: string;
  valorMandante: number | null;
  valorVisitante: number | null;
}) {
  const aMaior =
    typeof valorMandante === "number" && typeof valorVisitante === "number" && valorMandante > valorVisitante;
  const bMaior =
    typeof valorMandante === "number" && typeof valorVisitante === "number" && valorVisitante > valorMandante;

  return (
    <div className="grid grid-cols-3 border-t border-border px-1 py-3 text-sm first:border-t-0">
      <span className={`font-mono tabular-nums ${aMaior ? "font-semibold text-primary" : "text-muted-foreground"}`}>
        {valorOuTraco(valorMandante)}
      </span>
      <span className="text-center text-muted-foreground">{label}</span>
      <span
        className={`text-right font-mono tabular-nums ${bMaior ? "font-semibold text-primary" : "text-muted-foreground"}`}
      >
        {valorOuTraco(valorVisitante)}
      </span>
    </div>
  );
}

function TendenciaTexto({
  total,
  linhaReferencia,
  tendencia,
  unidade,
}: {
  total: number | null;
  linhaReferencia: number | null;
  tendencia: string | null;
  unidade: string;
}) {
  if (total === null || linhaReferencia === null || !tendencia) {
    return <p className="text-sm text-muted-foreground">Sem dado suficiente para calcular tendência.</p>;
  }

  const palavra = tendencia === "over" ? "mais de" : "menos de";

  return (
    <p className="text-sm text-muted-foreground">
      Tendência de{" "}
      <span className="font-mono font-semibold tabular-nums text-primary">
        {palavra} {linhaReferencia}
      </span>{" "}
      {unidade} na partida (total esperado:{" "}
      <span className="font-mono font-semibold tabular-nums text-primary">{total}</span>).
    </p>
  );
}

function ProjecaoPreJogoConteudo() {
  const searchParams = useSearchParams();
  const mandantePreSelecionado = searchParams.get("mandante") ?? "";

  const [times, setTimes] = useState<Time[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

  const [mandanteId, setMandanteId] = useState<string>(mandantePreSelecionado);
  const [visitanteId, setVisitanteId] = useState<string>("");

  const [projecao, setProjecao] = useState<Projecao | null>(null);
  const [carregandoProjecao, setCarregandoProjecao] = useState(false);
  const [erroProjecao, setErroProjecao] = useState<string | null>(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/times/")
      .then((resposta) => {
        if (!resposta.ok) {
          throw new Error("Erro ao buscar times");
        }
        return resposta.json();
      })
      .then((dados) => {
        setTimes(dados);
        setCarregando(false);
      })
      .catch((err) => {
        setErro(err.message);
        setCarregando(false);
      });
  }, []);

  useEffect(() => {
    if (!mandanteId || !visitanteId || mandanteId === visitanteId) {
      setProjecao(null);
      return;
    }

    setCarregandoProjecao(true);
    setErroProjecao(null);

    fetch(`http://127.0.0.1:8000/projecoes/${mandanteId}/${visitanteId}`)
      .then((resposta) => {
        if (!resposta.ok) {
          throw new Error("Erro ao buscar projeção");
        }
        return resposta.json();
      })
      .then((dados) => {
        setProjecao(dados);
        setCarregandoProjecao(false);
      })
      .catch((err) => {
        setErroProjecao(err.message);
        setCarregandoProjecao(false);
      });
  }, [mandanteId, visitanteId]);

  if (carregando) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background text-muted-foreground">
        <p>Carregando times...</p>
      </main>
    );
  }

  if (erro) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background text-destructive">
        <p>Erro: {erro}</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-background px-6 py-10 text-foreground">
      <div className="mx-auto max-w-3xl">
        <Link href="/times" className="text-sm text-muted-foreground underline hover:text-primary">
          ← Voltar para a lista de times
        </Link>

        <h1 className="mt-4 font-heading text-2xl font-semibold uppercase tracking-wide sm:text-3xl">
          Projeção Pré-Jogo
        </h1>
        <p className="mt-2 text-muted-foreground">
          Selecione mandante e visitante para ver a projeção estatística do confronto.
        </p>

        <div className="mt-8 grid gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-2 block text-sm text-muted-foreground">Mandante</label>
            <select
              value={mandanteId}
              onChange={(e) => setMandanteId(e.target.value)}
              className="w-full rounded-lg border border-input bg-card px-4 py-2 text-foreground outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
            >
              <option value="">Selecione um time</option>
              {times.map((time) => (
                <option key={time.id} value={time.id}>
                  {time.nome}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-2 block text-sm text-muted-foreground">Visitante</label>
            <select
              value={visitanteId}
              onChange={(e) => setVisitanteId(e.target.value)}
              className="w-full rounded-lg border border-input bg-card px-4 py-2 text-foreground outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
            >
              <option value="">Selecione um time</option>
              {times.map((time) => (
                <option key={time.id} value={time.id}>
                  {time.nome}
                </option>
              ))}
            </select>
          </div>
        </div>

        {mandanteId && visitanteId && mandanteId === visitanteId && (
          <p className="mt-8 text-primary">Selecione dois times diferentes.</p>
        )}

        {carregandoProjecao && <p className="mt-8 text-muted-foreground">Calculando projeção...</p>}

        {erroProjecao && <p className="mt-8 text-destructive">Erro: {erroProjecao}</p>}

        {projecao && (
          <div className="mt-10 grid gap-6">
            <div className="rounded-lg border border-primary/30 bg-primary/5 p-6 text-center">
              <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">
                Placar mais provável
              </p>
              <div className="mt-3 grid grid-cols-[1fr_auto_1fr] items-center gap-2 sm:gap-4">
                <span className="truncate text-right font-heading text-sm uppercase tracking-wide sm:text-lg">
                  {projecao.time_mandante}
                </span>
                <span className="font-mono text-3xl font-bold tabular-nums text-primary sm:text-4xl">
                  {placarArredondado(projecao.gols.mandante)}–{placarArredondado(projecao.gols.visitante)}
                </span>
                <span className="truncate text-left font-heading text-sm uppercase tracking-wide sm:text-lg">
                  {projecao.time_visitante}
                </span>
              </div>
              <p className="mt-3 text-xs text-muted-foreground">
                Gols esperados (média): {valorOuTraco(projecao.gols.mandante)} x {valorOuTraco(projecao.gols.visitante)}
              </p>
              <p className="mt-1 text-xs text-muted-foreground">
                Referência: {projecao.data_referencia}
              </p>
            </div>

            <CartaoProjecao titulo="Probabilidade de resultado">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <p
                    className={`font-mono text-2xl font-bold tabular-nums ${corDoFavorito(projecao.resultado.vitoria_mandante, [projecao.resultado.empate, projecao.resultado.vitoria_visitante])}`}
                  >
                    {valorOuTraco(projecao.resultado.vitoria_mandante)}%
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">{projecao.time_mandante}</p>
                </div>
                <div>
                  <p
                    className={`font-mono text-2xl font-bold tabular-nums ${corDoFavorito(projecao.resultado.empate, [projecao.resultado.vitoria_mandante, projecao.resultado.vitoria_visitante])}`}
                  >
                    {valorOuTraco(projecao.resultado.empate)}%
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">Empate</p>
                </div>
                <div>
                  <p
                    className={`font-mono text-2xl font-bold tabular-nums ${corDoFavorito(projecao.resultado.vitoria_visitante, [projecao.resultado.vitoria_mandante, projecao.resultado.empate])}`}
                  >
                    {valorOuTraco(projecao.resultado.vitoria_visitante)}%
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">{projecao.time_visitante}</p>
                </div>
              </div>
            </CartaoProjecao>

            <CartaoProjecao titulo="Escanteios esperados">
              <LinhaComparativa
                label="Escanteios"
                valorMandante={projecao.escanteios.mandante}
                valorVisitante={projecao.escanteios.visitante}
              />
              <div className="mt-3 border-t border-border pt-3">
                <TendenciaTexto
                  total={projecao.escanteios.total}
                  linhaReferencia={projecao.escanteios.linha_referencia}
                  tendencia={projecao.escanteios.tendencia}
                  unidade="escanteios"
                />
              </div>
            </CartaoProjecao>

            <CartaoProjecao titulo="Cartões esperados">
              <LinhaComparativa
                label="Amarelos"
                valorMandante={projecao.cartoes.amarelos_mandante}
                valorVisitante={projecao.cartoes.amarelos_visitante}
              />
              <LinhaComparativa
                label="Vermelhos"
                valorMandante={projecao.cartoes.vermelhos_mandante}
                valorVisitante={projecao.cartoes.vermelhos_visitante}
              />
              <div className="mt-3 border-t border-border pt-3">
                <TendenciaTexto
                  total={projecao.cartoes.total}
                  linhaReferencia={projecao.cartoes.linha_referencia}
                  tendencia={projecao.cartoes.tendencia}
                  unidade="cartões"
                />
              </div>
            </CartaoProjecao>

            <CartaoProjecao titulo="Chutes esperados">
              <LinhaComparativa
                label="Chutes totais"
                valorMandante={projecao.chutes.totais_mandante}
                valorVisitante={projecao.chutes.totais_visitante}
              />
              <LinhaComparativa
                label="Chutes ao gol"
                valorMandante={projecao.chutes.ao_gol_mandante}
                valorVisitante={projecao.chutes.ao_gol_visitante}
              />
              <LinhaComparativa
                label="Chutes 1º tempo"
                valorMandante={projecao.chutes.primeiro_tempo_mandante}
                valorVisitante={projecao.chutes.primeiro_tempo_visitante}
              />
            </CartaoProjecao>
          </div>
        )}
      </div>
    </main>
  );
}

export default function ProjecaoPreJogo() {
  return (
    <Suspense
      fallback={
        <main className="flex min-h-screen items-center justify-center bg-background text-muted-foreground">
          <p>Carregando...</p>
        </main>
      }
    >
      <ProjecaoPreJogoConteudo />
    </Suspense>
  );
}