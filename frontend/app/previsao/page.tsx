"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import {
  ChevronLeft,
  ArrowLeftRight,
  Flag,
  RectangleVertical,
  Target,
  Percent,
  type LucideIcon,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

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
    total_geral: number | null;
    linha_referencia_geral: number | null;
    tendencia_geral: string | null;
    ao_gol_mandante: number | null;
    ao_gol_visitante: number | null;
    total_ao_gol: number | null;
    linha_referencia_ao_gol: number | null;
    tendencia_ao_gol: string | null;
    primeiro_tempo_mandante: number | null;
    primeiro_tempo_visitante: number | null;
  };
}

function formatarData(dataStr: string) {
  const partes = dataStr.split("-");
  if (partes.length === 3) {
    const [ano, mes, dia] = partes;
    return `${dia}/${mes}/${ano}`;
  }
  return dataStr;
}

function valorOuTraco(valor: number | null) {
  return valor === null || valor === undefined ? "—" : valor;
}

function percentual(valor: number | null) {
  return valor === null || valor === undefined ? "—" : valor.toFixed(2);
}

function arredondado(valor: number | null) {
  return valor === null || valor === undefined ? "—" : Math.round(valor);
}

function corDoFavorito(valor: number | null, outros: (number | null)[]) {
  if (valor === null) return "text-muted-foreground";
  const eMaior = outros.every((outro) => outro === null || valor >= outro);
  return eMaior ? "text-primary" : "text-muted-foreground";
}

const CATEGORIAS: Record<string, { borda: string; badge: string; icon: LucideIcon }> = {
  probabilidade: { borda: "border-t-primary", badge: "bg-primary/10 text-primary", icon: Percent },
  escanteios: { borda: "border-t-blue-500", badge: "bg-blue-500/10 text-blue-400", icon: Flag },
  cartoes: { borda: "border-t-amber-500", badge: "bg-amber-500/10 text-amber-400", icon: RectangleVertical },
  chutes: { borda: "border-t-violet-500", badge: "bg-violet-500/10 text-violet-400", icon: Target },
};

function CartaoProjecao({
  titulo,
  categoria,
  children,
}: {
  titulo: string;
  categoria: keyof typeof CATEGORIAS;
  children: React.ReactNode;
}) {
  const { borda, badge, icon: Icon } = CATEGORIAS[categoria];
  return (
    <Card className={`border-t-2 ${borda}`}>
      <CardHeader className="flex-row items-center gap-2 space-y-0">
        <span className={`flex size-6 shrink-0 items-center justify-center rounded-md ${badge}`}>
          <Icon className="size-3.5" />
        </span>
        <CardTitle className="text-xs uppercase tracking-wide text-muted-foreground">
          {titulo}
        </CardTitle>
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}

function BarraProbabilidade({
  mandante,
  empate,
  visitante,
}: {
  mandante: number | null;
  empate: number | null;
  visitante: number | null;
}) {
  if (mandante === null || empate === null || visitante === null) return null;

  return (
    <div className="mt-4 flex h-1.5 overflow-hidden rounded-full bg-muted">
      <div className="bg-primary" style={{ width: `${mandante}%` }} />
      <div className="bg-muted-foreground/40" style={{ width: `${empate}%` }} />
      <div className="bg-sky-500" style={{ width: `${visitante}%` }} />
    </div>
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
    <div className="grid grid-cols-3 items-baseline border-t border-border px-1 py-3 text-sm first:border-t-0">
      <div className={aMaior ? "text-primary" : "text-muted-foreground"}>
        <span className="font-mono text-base font-semibold tabular-nums">{arredondado(valorMandante)}</span>
        {valorMandante !== null && (
          <span className="ml-1 font-mono text-[11px] text-muted-foreground">({valorMandante})</span>
        )}
      </div>
      <span className="text-center text-muted-foreground">{label}</span>
      <div className={`text-right ${bMaior ? "text-primary" : "text-muted-foreground"}`}>
        {valorVisitante !== null && (
          <span className="mr-1 font-mono text-[11px] text-muted-foreground">({valorVisitante})</span>
        )}
        <span className="font-mono text-base font-semibold tabular-nums">{arredondado(valorVisitante)}</span>
      </div>
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
    return <p className="text-xs text-muted-foreground">Sem dado suficiente para calcular tendência.</p>;
  }

  const palavra = tendencia === "over" ? "mais de" : "menos de";

  return (
    <p className="text-xs text-muted-foreground">
      Tendência de{" "}
      <span className="font-mono font-semibold tabular-nums text-primary">
        {palavra} {linhaReferencia}
      </span>{" "}
      {unidade} na partida — média exata prevista:{" "}
      <span className="font-mono font-semibold tabular-nums text-primary">{total}</span>{" "}
      <span className="text-muted-foreground">(arredondado: {arredondado(total)})</span>.
    </p>
  );
}

function ProjecaoPreJogoConteudo() {
  const searchParams = useSearchParams();
  const mandantePreSelecionado = searchParams.get("mandante") ?? "";
  const visitantePreSelecionado = searchParams.get("visitante") ?? "";

  const [times, setTimes] = useState<Time[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

  const [mandanteId, setMandanteId] = useState<string>(mandantePreSelecionado);
  const [visitanteId, setVisitanteId] = useState<string>(visitantePreSelecionado);

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
      <main className="min-h-screen bg-background px-6 py-10 text-foreground">
        <div className="mx-auto max-w-3xl">
          <Skeleton className="h-4 w-40" />
          <Skeleton className="mt-4 h-8 w-64" />
          <div className="mt-8 grid gap-4 sm:grid-cols-2">
            <Skeleton className="h-10 w-full rounded-lg" />
            <Skeleton className="h-10 w-full rounded-lg" />
          </div>
        </div>
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
        <Link
          href="/brasileirao"
          className="inline-flex items-center gap-1 text-xs font-medium uppercase tracking-wide text-muted-foreground transition-colors hover:text-primary"
        >
          <ChevronLeft className="h-3.5 w-3.5" />
          Brasileirão
        </Link>

        <h1 className="mt-4 font-heading text-2xl font-semibold uppercase tracking-wide sm:text-3xl">
          Previsão de Jogos
        </h1>
        <p className="mt-2 text-muted-foreground">
          Selecione mandante e visitante para ver a previsão estatística do confronto.
        </p>
        <p className="mt-1 text-xs text-muted-foreground">
          Considera apenas jogos do Brasileirão Série A — os times também disputam outras
          competições (Copa do Brasil, Libertadores, Sul-Americana etc.), que não entram nesta conta.
        </p>

        <div className="mt-8 flex flex-col items-stretch gap-3 sm:flex-row sm:items-end">
          <div className="w-full">
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

          <button
            type="button"
            onClick={() => {
              setMandanteId(visitanteId);
              setVisitanteId(mandanteId);
            }}
            disabled={!mandanteId && !visitanteId}
            aria-label="Trocar mandante e visitante"
            title="Trocar mandante e visitante"
            className="flex size-9 shrink-0 items-center justify-center self-center rounded-full border border-border bg-card text-muted-foreground transition-colors hover:border-primary/40 hover:text-primary disabled:pointer-events-none disabled:opacity-40 sm:mb-1.5"
          >
            <ArrowLeftRight className="size-4" />
          </button>

          <div className="w-full">
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

        <p className="mt-3 text-xs text-muted-foreground">
          A previsão é específica para este mando de campo — trocar quem é mandante e quem é
          visitante muda o resultado, já que o aproveitamento em casa costuma ser diferente do
          aproveitamento fora.
        </p>

        {mandanteId && visitanteId && mandanteId === visitanteId && (
          <p className="mt-8 text-primary">Selecione dois times diferentes.</p>
        )}

        {carregandoProjecao && (
          <div className="mt-10 grid gap-6">
            <Skeleton className="h-32 w-full rounded-lg" />
            <Skeleton className="h-24 w-full rounded-lg" />
            <Skeleton className="h-24 w-full rounded-lg" />
          </div>
        )}

        {erroProjecao && <p className="mt-8 text-destructive">Erro: {erroProjecao}</p>}

        {projecao && (
          <div className="mt-10 grid gap-6">
            <div className="overflow-hidden rounded-lg border border-primary/30 bg-primary/5">
              <p className="pt-4 text-center text-xs uppercase tracking-[0.2em] text-muted-foreground">
                Placar mais provável
              </p>
              <div className="mt-3 grid grid-cols-[1fr_auto_1fr] divide-x divide-primary/20">
                <div className="flex items-center justify-end px-3 py-4">
                  <span className="truncate font-heading text-sm uppercase tracking-wide sm:text-lg">
                    {projecao.time_mandante}
                  </span>
                </div>
                <div className="flex items-center justify-center px-4 py-4">
                  <span className="font-mono text-3xl font-bold tabular-nums text-primary sm:text-4xl">
                    {arredondado(projecao.gols.mandante)}–{arredondado(projecao.gols.visitante)}
                  </span>
                </div>
                <div className="flex items-center justify-start px-3 py-4">
                  <span className="truncate font-heading text-sm uppercase tracking-wide sm:text-lg">
                    {projecao.time_visitante}
                  </span>
                </div>
              </div>
              <div className="border-t border-primary/20 px-4 py-3 text-center">
                <p className="text-xs text-muted-foreground">
                  Gols esperados (média): {valorOuTraco(projecao.gols.mandante)} x {valorOuTraco(projecao.gols.visitante)}
                </p>
                <p className="mt-1 text-xs text-muted-foreground">
                  Referência: {formatarData(projecao.data_referencia)}
                </p>
              </div>
            </div>

            <CartaoProjecao titulo="Probabilidade de resultado" categoria="probabilidade">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <p
                    className={`font-mono text-2xl font-bold tabular-nums ${corDoFavorito(projecao.resultado.vitoria_mandante, [projecao.resultado.empate, projecao.resultado.vitoria_visitante])}`}
                  >
                    {percentual(projecao.resultado.vitoria_mandante)}%
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">{projecao.time_mandante}</p>
                </div>
                <div>
                  <p
                    className={`font-mono text-2xl font-bold tabular-nums ${corDoFavorito(projecao.resultado.empate, [projecao.resultado.vitoria_mandante, projecao.resultado.vitoria_visitante])}`}
                  >
                    {percentual(projecao.resultado.empate)}%
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">Empate</p>
                </div>
                <div>
                  <p
                    className={`font-mono text-2xl font-bold tabular-nums ${corDoFavorito(projecao.resultado.vitoria_visitante, [projecao.resultado.vitoria_mandante, projecao.resultado.empate])}`}
                  >
                    {percentual(projecao.resultado.vitoria_visitante)}%
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">{projecao.time_visitante}</p>
                </div>
              </div>
              <BarraProbabilidade
                mandante={projecao.resultado.vitoria_mandante}
                empate={projecao.resultado.empate}
                visitante={projecao.resultado.vitoria_visitante}
              />
            </CartaoProjecao>

            <CartaoProjecao titulo="Escanteios esperados" categoria="escanteios">
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

            <CartaoProjecao titulo="Cartões esperados" categoria="cartoes">
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

            <CartaoProjecao titulo="Chutes esperados" categoria="chutes">
              <LinhaComparativa
                label="Chutes totais"
                valorMandante={projecao.chutes.totais_mandante}
                valorVisitante={projecao.chutes.totais_visitante}
              />
              <div className="border-t border-border pt-3 pb-1">
                <TendenciaTexto
                  total={projecao.chutes.total_geral}
                  linhaReferencia={projecao.chutes.linha_referencia_geral}
                  tendencia={projecao.chutes.tendencia_geral}
                  unidade="chutes"
                />
              </div>
              <LinhaComparativa
                label="Chutes ao gol"
                valorMandante={projecao.chutes.ao_gol_mandante}
                valorVisitante={projecao.chutes.ao_gol_visitante}
              />
              <div className="border-t border-border pt-3 pb-1">
                <TendenciaTexto
                  total={projecao.chutes.total_ao_gol}
                  linhaReferencia={projecao.chutes.linha_referencia_ao_gol}
                  tendencia={projecao.chutes.tendencia_ao_gol}
                  unidade="chutes ao gol"
                />
              </div>
              {/* Em stand-by: Highlightly não fornece chutes por tempo (1ºT).
                  Reativar quando encontrarmos uma fonte com esse detalhamento.
              <LinhaComparativa
                label="Chutes 1º tempo"
                valorMandante={projecao.chutes.primeiro_tempo_mandante}
                valorVisitante={projecao.chutes.primeiro_tempo_visitante}
              />
              */}
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
