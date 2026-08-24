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
import { SeletorCampeonato } from "@/components/seletor-campeonato";
import { VhSpinner } from "@/components/vh-spinner";
import { API_URL, CAMPEONATO_BRASILEIRAO_ID } from "@/lib/api";

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
    placares_mais_provaveis: { mandante: number; visitante: number; probabilidade: number }[];
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

  const [campeonatoId, setCampeonatoId] = useState<number | null>(null);
  const [times, setTimes] = useState<Time[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

  const [mandanteId, setMandanteId] = useState<string>(mandantePreSelecionado);
  const [visitanteId, setVisitanteId] = useState<string>(visitantePreSelecionado);

  const [projecao, setProjecao] = useState<Projecao | null>(null);
  const [carregandoProjecao, setCarregandoProjecao] = useState(false);
  const [erroProjecao, setErroProjecao] = useState<string | null>(null);

  // Se veio de um link com mandante pre-selecionado (ex.: "ver completa"
  // na pagina do time), descobre o campeonato dele primeiro -- pode ser
  // qualquer liga, nao so o Brasileirao. Senao, comeca no Brasileirao.
  useEffect(() => {
    if (!mandantePreSelecionado) {
      setCampeonatoId(CAMPEONATO_BRASILEIRAO_ID);
      return;
    }
    fetch(`${API_URL}/times/${mandantePreSelecionado}`)
      .then((r) => (r.ok ? r.json() : null))
      .then((time) => setCampeonatoId(time?.campeonato_id ?? CAMPEONATO_BRASILEIRAO_ID))
      .catch(() => setCampeonatoId(CAMPEONATO_BRASILEIRAO_ID));
    // eslint-disable-next-line react-hooks/exhaustive-deps -- so roda uma vez, no valor inicial da URL
  }, []);

  useEffect(() => {
    if (campeonatoId === null) return;

    fetch(`${API_URL}/times/?campeonato_id=${campeonatoId}`)
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
  }, [campeonatoId]);

  useEffect(() => {
    if (!mandanteId || !visitanteId || mandanteId === visitanteId) {
      setProjecao(null);
      return;
    }

    setCarregandoProjecao(true);
    setErroProjecao(null);

    fetch(`${API_URL}/projecoes/${mandanteId}/${visitanteId}`)
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
      <main className="flex min-h-screen items-center justify-center bg-background text-foreground">
        <VhSpinner />
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
          href={campeonatoId === CAMPEONATO_BRASILEIRAO_ID ? "/brasileirao" : `/campeonato/${campeonatoId}`}
          className="inline-flex items-center gap-1 text-xs font-medium uppercase tracking-wide text-muted-foreground transition-colors hover:text-primary"
        >
          <ChevronLeft className="h-3.5 w-3.5" />
          Voltar
        </Link>

        <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
          <h1 className="font-heading text-2xl font-semibold uppercase tracking-wide sm:text-3xl">
            Previsão de Jogos
          </h1>
          <SeletorCampeonato
            value={campeonatoId ?? CAMPEONATO_BRASILEIRAO_ID}
            onChange={(id) => {
              setCampeonatoId(id);
              setMandanteId("");
              setVisitanteId("");
            }}
          />
        </div>
        <p className="mt-2 text-muted-foreground">
          Selecione mandante e visitante para ver a previsão estatística do confronto.
        </p>
        <p className="mt-1 text-xs text-muted-foreground">
          Considera apenas jogos do campeonato selecionado — os times também disputam outras
          competições, que não entram nesta conta.
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
          <div className="mt-10 flex min-h-40 items-center justify-center">
            <VhSpinner />
          </div>
        )}

        {erroProjecao && <p className="mt-8 text-destructive">Erro: {erroProjecao}</p>}

        {projecao && (
          <div className="mt-10 grid gap-6">
            <div className="overflow-hidden rounded-lg border border-primary/30 bg-primary/5">
              <p className="pt-4 text-center text-xs uppercase tracking-[0.2em] text-muted-foreground">
                Placares mais prováveis
              </p>
              <div className="mt-2 grid grid-cols-[1fr_auto_1fr] items-center gap-x-2 px-4 text-xs text-muted-foreground sm:text-sm">
                <span className="truncate text-right font-heading uppercase tracking-wide">
                  {projecao.time_mandante}
                </span>
                <span />
                <span className="truncate text-left font-heading uppercase tracking-wide">
                  {projecao.time_visitante}
                </span>
              </div>

              {projecao.gols.placares_mais_provaveis.length === 0 ? (
                <p className="px-4 py-6 text-center text-sm text-muted-foreground">
                  Histórico insuficiente pra estimar um placar.
                </p>
              ) : (
                <ul className="mt-1 divide-y divide-primary/10">
                  {projecao.gols.placares_mais_provaveis.map((placar, index) => (
                    <li
                      key={`${placar.mandante}-${placar.visitante}`}
                      className={`flex items-center gap-3 px-4 py-2.5 ${index === 0 ? "bg-primary/5" : ""}`}
                    >
                      <span className="w-4 shrink-0 text-center font-mono text-[10px] text-muted-foreground">
                        {index + 1}º
                      </span>
                      <span
                        className={`shrink-0 font-mono tabular-nums text-primary ${index === 0 ? "text-2xl font-bold sm:text-3xl" : "text-base font-semibold"}`}
                      >
                        {placar.mandante}–{placar.visitante}
                      </span>
                      <div className="min-w-0 flex-1">
                        <div className="h-1.5 w-full overflow-hidden rounded-full bg-primary/10">
                          <div
                            className="h-full rounded-full bg-primary"
                            style={{ width: `${Math.min(placar.probabilidade * 100 * 4, 100)}%` }}
                          />
                        </div>
                      </div>
                      <span className="shrink-0 font-mono text-xs tabular-nums text-muted-foreground">
                        {(placar.probabilidade * 100).toFixed(1)}%
                      </span>
                    </li>
                  ))}
                </ul>
              )}

              <div className="border-t border-primary/20 px-4 py-3 text-center">
                <p className="text-xs text-muted-foreground">
                  Nenhum placar isolado passa de ~20% — são muitos resultados possíveis, isto é só o topo da lista.
                </p>
                <p className="mt-1 text-xs text-muted-foreground">
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
