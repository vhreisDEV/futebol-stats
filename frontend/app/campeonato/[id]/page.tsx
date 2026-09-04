"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ChevronLeft, ChevronRight, TrendingUp, Users, UserRound, Flame, Shield } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Classificacao } from "@/components/classificacao";
import { PartidaModal } from "@/components/partida-modal";
import { VhSpinner } from "@/components/vh-spinner";
import { NavChip } from "@/components/nav-chip";
import { API_URL, CAMPEONATO_BRASILEIRAO_ID, RODADA_MINIMA_FUNCOES_AVANCADAS } from "@/lib/api";
import { formatarDataHora } from "@/lib/formatar-data";
import { flagSrc } from "@/lib/paises";

interface Campeonato {
  id: number;
  nome: string;
  pais_nome: string;
  pais_codigo: string;
  temporada_label: string;
  total_times: number;
}

interface PartidaRodada {
  id: number;
  data: string | null;
  hora: string | null;
  status: string;
  time_mandante_id: number;
  time_mandante: string;
  time_visitante_id: number;
  time_visitante: string;
  gols_mandante: number | null;
  gols_visitante: number | null;
}

interface RodadaResponse {
  rodada: number;
  partidas: PartidaRodada[];
}

interface RodadaAtualResponse {
  rodada_atual: number;
  rodada_maxima: number;
}

export default function CampeonatoPage() {
  const params = useParams();
  const campeonatoId = Number(params.id);

  const [campeonato, setCampeonato] = useState<Campeonato | null>(null);
  const [rodadaAtual, setRodadaAtual] = useState<number | null>(null);
  const [rodadaMaxima, setRodadaMaxima] = useState<number | null>(null);
  const [rodadaSelecionada, setRodadaSelecionada] = useState<number | null>(null);
  const [partidas, setPartidas] = useState<PartidaRodada[]>([]);
  const [carregandoInicial, setCarregandoInicial] = useState(true);
  const [carregandoRodada, setCarregandoRodada] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [partidaAbertaId, setPartidaAbertaId] = useState<number | null>(null);
  const [direcao, setDirecao] = useState<"next" | "prev">("next");

  useEffect(() => {
    if (!campeonatoId) return;

    fetch(`${API_URL}/campeonatos/${campeonatoId}`)
      .then((r) => {
        if (!r.ok) throw new Error("Campeonato não encontrado");
        return r.json();
      })
      .then((dadosCampeonato: Campeonato) => {
        setCampeonato(dadosCampeonato);

        if (dadosCampeonato.total_times === 0) {
          setCarregandoInicial(false);
          return null;
        }

        return fetch(`${API_URL}/rodadas/atual?campeonato_id=${campeonatoId}`).then((r) => {
          if (!r.ok) throw new Error("Erro ao buscar a rodada atual");
          return r.json();
        });
      })
      .then((dadosRodada: RodadaAtualResponse | null) => {
        if (!dadosRodada) return;
        setRodadaAtual(dadosRodada.rodada_atual);
        setRodadaMaxima(dadosRodada.rodada_maxima);
        setRodadaSelecionada(dadosRodada.rodada_atual);
        setCarregandoInicial(false);
      })
      .catch((err) => {
        setErro(err.message);
        setCarregandoInicial(false);
      });
  }, [campeonatoId]);

  useEffect(() => {
    if (rodadaSelecionada === null) return;

    setCarregandoRodada(true);

    fetch(`${API_URL}/rodadas/${rodadaSelecionada}?campeonato_id=${campeonatoId}`)
      .then((r) => {
        if (r.status === 404) return { rodada: rodadaSelecionada, partidas: [] };
        if (!r.ok) throw new Error("Erro ao buscar a rodada");
        return r.json();
      })
      .then((dados: RodadaResponse) => {
        setPartidas(dados.partidas);
        setCarregandoRodada(false);
      })
      .catch((err) => {
        setErro(err.message);
        setCarregandoRodada(false);
      });
  }, [rodadaSelecionada, campeonatoId]);

  if (erro) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background text-destructive">
        <p>Erro: {erro}</p>
      </main>
    );
  }

  if (!carregandoInicial && campeonato && campeonato.total_times === 0) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background px-4 text-foreground">
        <div className="mx-auto max-w-sm text-center">
          <Link
            href="/"
            className="font-heading text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground transition-colors hover:text-primary"
          >
            VEAGA
          </Link>
          <h1 className="mt-3 flex items-center justify-center gap-2 font-heading text-xl font-semibold uppercase tracking-wide">
            {/* eslint-disable-next-line @next/next/no-img-element -- SVG local, decorativo, sem necessidade de otimizacao do Next/Image */}
            <img src={flagSrc(campeonato.pais_codigo)} alt="" className="h-[0.75em] w-auto rounded-sm" />
            {campeonato.nome} {campeonato.temporada_label}
          </h1>
          <p className="mt-4 text-sm text-muted-foreground">
            Essa liga ainda está em desenvolvimento no VEAGA — os dados completos chegam em breve.
          </p>
        </div>
      </main>
    );
  }

  if (carregandoInicial || rodadaSelecionada === null || rodadaMaxima === null || !campeonato) {
    return (
      <main className="min-h-screen bg-background px-4 py-8 text-foreground sm:px-6 sm:py-10">
        <div className="mx-auto max-w-5xl">
          <div className="flex min-h-[50vh] items-center justify-center">
            <VhSpinner />
          </div>
        </div>
      </main>
    );
  }

  const funcoesAvancadasLiberadas =
    rodadaAtual !== null && rodadaAtual >= RODADA_MINIMA_FUNCOES_AVANCADAS;
  const rodadasParaLiberar = rodadaAtual === null ? RODADA_MINIMA_FUNCOES_AVANCADAS : RODADA_MINIMA_FUNCOES_AVANCADAS - rodadaAtual;

  return (
    <main className="min-h-screen bg-background px-4 py-8 text-foreground sm:px-6 sm:py-10">
      <div className="mx-auto max-w-5xl">
        <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-3">
          <div>
            <Link
              href="/"
              className="font-heading text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground transition-colors hover:text-primary"
            >
              VEAGA
            </Link>
            <h1 className="mt-2 flex items-center gap-2 font-heading text-2xl font-semibold uppercase tracking-wide sm:text-3xl">
              {/* eslint-disable-next-line @next/next/no-img-element -- SVG local, decorativo, sem necessidade de otimizacao do Next/Image */}
              <img src={flagSrc(campeonato.pais_codigo)} alt="" className="h-[0.75em] w-auto rounded-sm" />
              {campeonato.nome} {campeonato.temporada_label}
            </h1>
            {!funcoesAvancadasLiberadas && (
              <p className="mt-1 text-xs text-muted-foreground">
                Previsão de Jogos, Dicas da Rodada e Comparar Times liberam a partir da
                rodada {RODADA_MINIMA_FUNCOES_AVANCADAS} dessa liga (faltam {rodadasParaLiberar}{" "}
                rodada{rodadasParaLiberar === 1 ? "" : "s"}).
              </p>
            )}
          </div>

          <div className="flex flex-wrap gap-2">
            {funcoesAvancadasLiberadas && (
              <>
                <NavChip
                  href={`/previsao?campeonato=${campeonatoId}`}
                  label="Previsão de Jogos"
                  icon={TrendingUp}
                  cor="gold"
                />
                <NavChip href={`/dicas?campeonato=${campeonatoId}`} label="Dicas da Rodada" icon={Flame} cor="emerald" />
                <NavChip href={`/comparar?campeonato=${campeonatoId}`} label="Comparar Times" icon={Users} cor="rose" />
              </>
            )}
            <NavChip href={`/times?campeonato=${campeonatoId}`} label="Times" icon={Shield} cor="orange" />
            <NavChip
              href={`/jogadores?campeonato=${campeonatoId}`}
              label="Jogadores"
              icon={UserRound}
              cor="neutral"
            />
          </div>
        </div>

        <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2 lg:items-start">
          <section>
            <h2 className="font-heading text-sm font-semibold uppercase tracking-wide text-muted-foreground">
              Classificação
            </h2>
            <p className="mt-1 text-xs text-muted-foreground">
              Posição atual do campeonato (considera jogos atrasados).
            </p>
            <div className="mt-3">
              <Classificacao campeonatoId={campeonatoId} />
            </div>
          </section>

          <section>
            <div className="mx-auto flex w-fit items-stretch overflow-hidden rounded-lg border border-border bg-card">
              <button
                type="button"
                disabled={rodadaSelecionada <= 1}
                onClick={() => {
                  setDirecao("prev");
                  setCarregandoRodada(true);
                  setRodadaSelecionada((r) => (r ?? 1) - 1);
                }}
                aria-label="Rodada anterior"
                className="flex items-center justify-center px-3 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground disabled:pointer-events-none disabled:opacity-30"
              >
                <ChevronLeft className="size-4" />
              </button>

              <div className="flex flex-col items-center justify-center border-x border-border px-6 py-1.5">
                <span className="text-[10px] font-medium uppercase tracking-[0.2em] text-muted-foreground">
                  Rodada
                </span>
                <span className="font-mono text-xl font-bold tabular-nums text-primary sm:text-2xl">
                  {rodadaSelecionada}
                  <span className="text-xs font-normal text-muted-foreground sm:text-sm"> / {rodadaMaxima}</span>
                </span>
              </div>

              <button
                type="button"
                disabled={rodadaSelecionada >= rodadaMaxima}
                onClick={() => {
                  setDirecao("next");
                  setCarregandoRodada(true);
                  setRodadaSelecionada((r) => (r ?? 1) + 1);
                }}
                aria-label="Próxima rodada"
                className="flex items-center justify-center px-3 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground disabled:pointer-events-none disabled:opacity-30"
              >
                <ChevronRight className="size-4" />
              </button>
            </div>

            <p className="mt-2 text-center text-xs text-muted-foreground">
              Toque em uma partida para ver os detalhes.
            </p>

            {carregandoRodada ? (
              <div
                key={`spinner-${rodadaSelecionada}`}
                className={`animate-in fade-in mt-3 flex min-h-40 items-center justify-center duration-300 motion-reduce:animate-none ${direcao === "next" ? "slide-in-from-right-4" : "slide-in-from-left-4"}`}
              >
                <VhSpinner />
              </div>
            ) : partidas.length === 0 ? (
              <p className="py-8 text-center text-muted-foreground">
                Nenhuma partida cadastrada para essa rodada ainda.
              </p>
            ) : (
              <div
                key={`conteudo-${rodadaSelecionada}`}
                className="animate-in fade-in mt-3 grid gap-1 duration-300 motion-reduce:animate-none"
              >
                {(() => {
                  const dentroDaJanela =
                    rodadaAtual !== null && rodadaSelecionada !== null && rodadaSelecionada <= rodadaAtual + 1;
                  return partidas.map((partida) => (
                    <Card
                      key={partida.id}
                      size="sm"
                      onClick={() => setPartidaAbertaId(partida.id)}
                      className="cursor-pointer overflow-hidden ring-0 transition-colors hover:bg-muted/50"
                    >
                      <CardContent className="py-0.5">
                        <p className="text-center text-[9px] uppercase tracking-wide text-muted-foreground">
                          {formatarDataHora(partida.data, partida.hora)}
                        </p>
                        <div className="mt-0.5 flex items-center justify-center gap-2">
                          <div className="min-w-0 flex-1 text-right">
                            <Link
                              href={`/times/${partida.time_mandante_id}`}
                              onClick={(e) => e.stopPropagation()}
                              className="inline-block max-w-full truncate text-sm font-medium transition-colors hover:text-primary"
                            >
                              {partida.time_mandante}
                            </Link>
                          </div>
                          {partida.status === "adiada" ? (
                            <span className="shrink-0 text-[10px] font-bold uppercase tracking-wide text-amber-400">
                              Adiado
                            </span>
                          ) : partida.status === "agendada" ? (
                            <span className="shrink-0 text-[10px] uppercase tracking-wide text-muted-foreground">
                              A jogar
                            </span>
                          ) : (
                            <div className="flex shrink-0 items-center gap-1 font-mono text-sm font-semibold tabular-nums text-primary">
                              <span>{partida.gols_mandante}</span>
                              <span className="text-xs text-muted-foreground">–</span>
                              <span>{partida.gols_visitante}</span>
                            </div>
                          )}
                          <div className="min-w-0 flex-1 text-left">
                            <Link
                              href={`/times/${partida.time_visitante_id}`}
                              onClick={(e) => e.stopPropagation()}
                              className="inline-block max-w-full truncate text-sm font-medium transition-colors hover:text-primary"
                            >
                              {partida.time_visitante}
                            </Link>
                          </div>
                        </div>
                        {partida.status === "agendada" &&
                          dentroDaJanela &&
                          campeonatoId === CAMPEONATO_BRASILEIRAO_ID && (
                          <Link
                            href={`/analise/${partida.id}`}
                            onClick={(e) => e.stopPropagation()}
                            className="mt-0.5 block text-center text-[9px] font-semibold uppercase tracking-wide text-violet-400 hover:text-violet-300"
                          >
                            ✨ Ver análise da IA
                          </Link>
                        )}
                      </CardContent>
                    </Card>
                  ));
                })()}
              </div>
            )}
          </section>
        </div>
      </div>

      <PartidaModal partidaId={partidaAbertaId} onClose={() => setPartidaAbertaId(null)} />
    </main>
  );
}
