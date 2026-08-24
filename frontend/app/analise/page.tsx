"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ChevronLeft, ChevronRight, Sparkles, TrendingUp, Lock } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { VhSpinner } from "@/components/vh-spinner";
import { ListaDestaques, fraseDestaque, type Destaque } from "@/components/lista-destaques";
import { SeletorCampeonato } from "@/components/seletor-campeonato";
import { API_URL, CAMPEONATO_BRASILEIRAO_ID } from "@/lib/api";
import { formatarDataHora } from "@/lib/formatar-data";

interface PartidaRodada {
  id: number;
  data: string | null;
  hora: string | null;
  status: string;
  rodada: number | null;
  time_mandante: string;
  time_visitante: string;
}

interface RodadaResponse {
  rodada: number;
  partidas: PartidaRodada[];
}

interface RodadaAtualResponse {
  rodada_atual: number;
  rodada_maxima: number;
}

interface MelhorMercado {
  time: "mandante" | "visitante";
  nome_time: string;
  destaque: Destaque;
}

interface AnaliseResponse {
  disponivel: boolean;
  texto: string | null;
  destaques_mandante: Destaque[];
  destaques_visitante: Destaque[];
  melhor_mercado: MelhorMercado | null;
}

interface JogoComAnalise {
  partida: PartidaRodada;
  analise: AnaliseResponse;
}

export default function AnaliseIA() {
  const [campeonatoId, setCampeonatoId] = useState(CAMPEONATO_BRASILEIRAO_ID);
  const [rodadaMaxima, setRodadaMaxima] = useState<number | null>(null);
  const [rodadaSelecionada, setRodadaSelecionada] = useState<number | null>(null);
  const [jogos, setJogos] = useState<JogoComAnalise[]>([]);
  const [carregandoRodada, setCarregandoRodada] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    setCarregandoRodada(true);

    fetch(`${API_URL}/rodadas/atual?campeonato_id=${campeonatoId}`)
      .then((r) => {
        if (!r.ok) throw new Error("Erro ao buscar a rodada atual");
        return r.json();
      })
      .then((dados: RodadaAtualResponse) => {
        setRodadaMaxima(dados.rodada_maxima);
        setRodadaSelecionada(dados.rodada_atual);
      })
      .catch((err) => {
        setErro(err.message);
        setCarregandoRodada(false);
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
        const agendadas = dados.partidas.filter((p) => p.status === "agendada");
        return Promise.all(
          agendadas.map((partida) =>
            fetch(`${API_URL}/partidas/${partida.id}/analise`)
              .then((r) => r.json())
              .then((analise: AnaliseResponse) => ({ partida, analise }))
          )
        );
      })
      .then((combinados: JogoComAnalise[]) => {
        setJogos(combinados);
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

  if (rodadaMaxima === null) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background text-foreground">
        <VhSpinner />
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-background px-4 py-8 text-foreground sm:px-6 sm:py-10">
      <div className="mx-auto max-w-3xl">
        <Link
          href={campeonatoId === CAMPEONATO_BRASILEIRAO_ID ? "/brasileirao" : `/campeonato/${campeonatoId}`}
          className="inline-flex items-center gap-1 text-xs font-medium uppercase tracking-wide text-muted-foreground transition-colors hover:text-primary"
        >
          <ChevronLeft className="h-3.5 w-3.5" />
          Voltar
        </Link>

        <div className="mt-2 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Sparkles className="size-6 text-violet-400" />
            <h1 className="font-heading text-2xl font-semibold uppercase tracking-wide sm:text-3xl">
              Análise IA
            </h1>
          </div>
          <SeletorCampeonato value={campeonatoId} onChange={setCampeonatoId} />
        </div>
        <p className="mt-1 text-sm text-muted-foreground">
          Mercados em que cada time vem se destacando (mando de campo já considerado), com o melhor palpite
          apontado pela IA.
        </p>

        <div className="mx-auto mt-6 flex w-fit items-stretch overflow-hidden rounded-lg border border-border bg-card">
          <button
            type="button"
            disabled={rodadaSelecionada === null || rodadaSelecionada <= 1}
            onClick={() => setRodadaSelecionada((r) => (r ?? 1) - 1)}
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
            disabled={rodadaSelecionada === null || rodadaSelecionada >= rodadaMaxima}
            onClick={() => setRodadaSelecionada((r) => (r ?? 1) + 1)}
            aria-label="Próxima rodada"
            className="flex items-center justify-center px-3 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground disabled:pointer-events-none disabled:opacity-30"
          >
            <ChevronRight className="size-4" />
          </button>
        </div>

        {carregandoRodada ? (
          <div className="mt-8 flex min-h-40 items-center justify-center">
            <VhSpinner />
          </div>
        ) : jogos.length === 0 ? (
          <div className="mt-8 rounded-lg border border-dashed border-border p-8 text-center text-sm text-muted-foreground">
            Nenhuma partida a acontecer nessa rodada.
          </div>
        ) : (
          <div className="mt-6 grid gap-3">
            {jogos.map(({ partida, analise }) => {
              const nomeDoTimeDoMercado =
                analise.melhor_mercado?.time === "mandante" ? partida.time_mandante : partida.time_visitante;
              const mandoDoMercado = analise.melhor_mercado?.time === "mandante" ? "em casa" : "fora de casa";

              return (
                <Card key={partida.id} className="overflow-hidden border-primary/15">
                  <CardContent>
                    <p className="text-center text-xs uppercase tracking-wide text-muted-foreground">
                      {formatarDataHora(partida.data, partida.hora)}
                    </p>
                    <p className="mt-1 text-center font-heading text-base font-semibold uppercase tracking-wide">
                      {partida.time_mandante}
                      <span className="mx-2 text-muted-foreground">x</span>
                      {partida.time_visitante}
                    </p>

                    {analise.melhor_mercado && (
                      <div className="mt-4 rounded-lg border border-violet-500/30 bg-violet-500/10 p-3">
                        <div className="flex items-center gap-1.5">
                          <TrendingUp className="size-3.5 text-violet-400" />
                          <span className="text-[10px] font-bold uppercase tracking-wide text-violet-400">
                            Melhor mercado
                          </span>
                          <span className="ml-auto rounded-full bg-violet-500/20 px-2 py-0.5 text-[9px] font-bold uppercase tracking-wide text-violet-300">
                            {Math.round(analise.melhor_mercado.destaque.taxa * 100)}%
                          </span>
                        </div>
                        <p className="mt-1.5 text-sm text-foreground">
                          {fraseDestaque(nomeDoTimeDoMercado, mandoDoMercado, analise.melhor_mercado.destaque)}
                        </p>
                      </div>
                    )}

                    <div className="mt-4 grid gap-4 sm:grid-cols-2 sm:divide-x sm:divide-border">
                      <div className="min-w-0">
                        <p className="text-[10px] font-medium uppercase tracking-wide text-muted-foreground/70">
                          {partida.time_mandante} em casa
                        </p>
                        <div className="mt-1.5">
                          <ListaDestaques
                            time={partida.time_mandante}
                            mandoLabel="em casa"
                            destaques={analise.destaques_mandante}
                          />
                        </div>
                      </div>
                      <div className="min-w-0 sm:pl-4">
                        <p className="text-[10px] font-medium uppercase tracking-wide text-muted-foreground/70">
                          {partida.time_visitante} fora
                        </p>
                        <div className="mt-1.5">
                          <ListaDestaques
                            time={partida.time_visitante}
                            mandoLabel="fora de casa"
                            destaques={analise.destaques_visitante}
                          />
                        </div>
                      </div>
                    </div>

                    <Link
                      href={`/analise/${partida.id}`}
                      className="mt-4 flex items-center gap-2 rounded-md border border-violet-500/30 bg-violet-500/5 p-3 transition-colors hover:bg-violet-500/10"
                    >
                      <span className="flex size-6 shrink-0 items-center justify-center rounded-full bg-violet-500/15 text-violet-400">
                        <Lock className="size-3" />
                      </span>
                      <span className="min-w-0 flex-1 text-xs leading-relaxed text-muted-foreground">
                        {analise.disponivel && analise.texto
                          ? analise.texto.slice(0, 90).trim() + "…"
                          : "A análise completa dessa partida está em preparação."}
                      </span>
                      <span className="shrink-0 rounded-full bg-violet-500/15 px-2 py-0.5 text-[9px] font-bold uppercase tracking-wide text-violet-400">
                        PRO
                      </span>
                    </Link>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </main>
  );
}
