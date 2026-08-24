"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ChevronLeft, ChevronRight, TrendingUp, Users, Shield, UserRound, Flame, Sparkles } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Classificacao } from "@/components/classificacao";
import { PartidaModal } from "@/components/partida-modal";
import { NavChip } from "@/components/nav-chip";
import { VhSpinner } from "@/components/vh-spinner";
import { API_URL, CAMPEONATO_BRASILEIRAO_ID } from "@/lib/api";
import { formatarDataHora } from "@/lib/formatar-data";
import { flagSrc } from "@/lib/paises";

interface Campeonato {
  id: number;
  nome: string;
  pais_nome: string;
  pais_codigo: string;
  temporada_label: string;
}

function CabecalhoCampeonato() {
  const [campeonato, setCampeonato] = useState<Campeonato | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/campeonatos/${CAMPEONATO_BRASILEIRAO_ID}`)
      .then((r) => (r.ok ? r.json() : null))
      .then(setCampeonato)
      .catch(() => {});
  }, []);

  const titulo = campeonato ? `${campeonato.nome} ${campeonato.temporada_label}` : "Brasileirão Série A 2026";

  return (
    <div>
      <Link
        href="/"
        className="font-heading text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground transition-colors hover:text-primary"
      >
        VEAGA
      </Link>
      <h1 className="mt-2 flex items-center gap-2 font-heading text-2xl font-semibold uppercase tracking-wide sm:text-3xl">
        {campeonato && (
          // eslint-disable-next-line @next/next/no-img-element -- SVG local, decorativo, sem necessidade de otimizacao do Next/Image
          <img src={flagSrc(campeonato.pais_codigo)} alt="" className="h-[0.75em] w-auto rounded-sm" />
        )}
        {titulo}
      </h1>
    </div>
  );
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

export default function Brasileirao() {
  const [rodadaMaxima, setRodadaMaxima] = useState<number | null>(null);
  const [rodadaSelecionada, setRodadaSelecionada] = useState<number | null>(null);
  const [partidas, setPartidas] = useState<PartidaRodada[]>([]);
  const [carregandoInicial, setCarregandoInicial] = useState(true);
  const [carregandoRodada, setCarregandoRodada] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [partidaAbertaId, setPartidaAbertaId] = useState<number | null>(null);
  const [direcao, setDirecao] = useState<"next" | "prev">("next");

  useEffect(() => {
    fetch(`${API_URL}/rodadas/atual?campeonato_id=${CAMPEONATO_BRASILEIRAO_ID}`)
      .then((r) => {
        if (!r.ok) throw new Error("Erro ao buscar a rodada atual");
        return r.json();
      })
      .then((dados: RodadaAtualResponse) => {
        setRodadaMaxima(dados.rodada_maxima);
        setRodadaSelecionada(dados.rodada_atual);
        setCarregandoInicial(false);
      })
      .catch((err) => {
        setErro(err.message);
        setCarregandoInicial(false);
      });
  }, []);

  useEffect(() => {
    if (rodadaSelecionada === null) return;

    setCarregandoRodada(true);

    fetch(`${API_URL}/rodadas/${rodadaSelecionada}?campeonato_id=${CAMPEONATO_BRASILEIRAO_ID}`)
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
  }, [rodadaSelecionada]);

  if (erro) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background text-destructive">
        <p>Erro: {erro}</p>
      </main>
    );
  }

  if (carregandoInicial || rodadaSelecionada === null || rodadaMaxima === null) {
    return (
      <main className="min-h-screen bg-background px-4 py-8 text-foreground sm:px-6 sm:py-10">
        <div className="mx-auto max-w-5xl">
          <CabecalhoCampeonato />

          <div className="flex min-h-[50vh] items-center justify-center">
            <VhSpinner />
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-background px-4 py-8 text-foreground sm:px-6 sm:py-10">
      <div className="mx-auto max-w-5xl">
        <div className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
          <CabecalhoCampeonato />
          <div className="flex w-full shrink-0 flex-wrap gap-2 sm:w-auto">
            <NavChip href="/previsao" label="Previsão de Jogos" icon={TrendingUp} cor="gold" />
            <NavChip href="/dicas" label="Dicas da Rodada" icon={Flame} cor="emerald" />
            <NavChip href="/analise" label="Análise IA" icon={Sparkles} cor="violet" />
            <NavChip href="/comparar" label="Comparar Times" icon={Users} cor="rose" />
            <NavChip href="/times" label="Times" icon={Shield} cor="orange" />
            <NavChip href="/jogadores" label="Jogadores" icon={UserRound} cor="neutral" />
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
              <Classificacao />
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
                {partidas.map((partida) => (
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
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </section>
        </div>
      </div>

      <PartidaModal partidaId={partidaAbertaId} onClose={() => setPartidaAbertaId(null)} />
    </main>
  );
}
