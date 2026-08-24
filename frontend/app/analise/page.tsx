"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ChevronLeft, ChevronRight, Sparkles, ChevronDown, ExternalLink, Trophy } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { VhSpinner } from "@/components/vh-spinner";
import { ListaDestaques, type Destaque } from "@/components/lista-destaques";
import { BilheteSimplesCard, BilheteMultiplaCard, fraseCurta, type Perna } from "@/components/bilhete-card";
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

interface BilheteSimples {
  perna: Perna;
  confianca: number;
}

interface BilheteMultipla {
  pernas: Perna[];
  confianca_combinada: number;
}

interface AnaliseResponse {
  disponivel: boolean;
  resumo: string | null;
  destaques_mandante: Destaque[];
  destaques_visitante: Destaque[];
  bilhete_simples: BilheteSimples | null;
  bilhete_multipla: BilheteMultipla | null;
}

interface JogoComAnalise {
  partida: PartidaRodada;
  analise: AnaliseResponse;
}

const MAX_MELHORES_PALPITES = 5;

function CartaoMelhoresPalpites({ jogos }: { jogos: JogoComAnalise[] }) {
  const top = jogos
    .filter((j) => j.analise.bilhete_simples)
    .sort((a, b) => b.analise.bilhete_simples!.confianca - a.analise.bilhete_simples!.confianca)
    .slice(0, MAX_MELHORES_PALPITES);

  if (top.length < 2) return null;

  return (
    <Card className="overflow-hidden border-primary/30 bg-primary/5">
      <CardContent>
        <div className="flex items-center gap-2">
          <Trophy className="size-5 text-primary" />
          <h2 className="font-heading text-sm font-semibold uppercase tracking-wide text-foreground">
            Melhores palpites da rodada
          </h2>
        </div>
        <ol className="mt-3 grid gap-1.5">
          {top.map(({ partida, analise }, i) => (
            <li key={partida.id}>
              <Link
                href={`/analise/${partida.id}`}
                className="flex items-center gap-2.5 rounded-md bg-card px-3 py-2 ring-1 ring-foreground/10 transition-colors hover:ring-primary/40"
              >
                <span className="flex size-5 shrink-0 items-center justify-center rounded-full bg-primary/15 font-mono text-[10px] font-bold text-primary">
                  {i + 1}
                </span>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-[10px] uppercase tracking-wide text-muted-foreground">
                    {partida.time_mandante} x {partida.time_visitante}
                  </p>
                  <p className="truncate text-sm font-medium text-foreground">
                    {fraseCurta(analise.bilhete_simples!.perna)}
                  </p>
                </div>
                <span className="shrink-0 rounded-full bg-primary/15 px-2 py-0.5 font-mono text-xs font-bold tabular-nums text-primary">
                  {analise.bilhete_simples!.confianca.toFixed(1)}/10
                </span>
              </Link>
            </li>
          ))}
        </ol>
      </CardContent>
    </Card>
  );
}

function CardPartida({ partida, analise }: JogoComAnalise) {
  const [mercadosAbertos, setMercadosAbertos] = useState(false);

  return (
    <Card className="overflow-hidden border-primary/15">
      <CardContent>
        <p className="text-center text-xs uppercase tracking-wide text-muted-foreground">
          {formatarDataHora(partida.data, partida.hora)}
        </p>
        <p className="mt-1 text-center font-heading text-base font-semibold uppercase tracking-wide">
          {partida.time_mandante}
          <span className="mx-2 text-muted-foreground">x</span>
          {partida.time_visitante}
        </p>

        {(analise.bilhete_simples || analise.bilhete_multipla) && (
          <div className="mt-4 grid gap-2">
            {analise.bilhete_simples && (
              <BilheteSimplesCard
                perna={analise.bilhete_simples.perna}
                confianca={analise.bilhete_simples.confianca}
              />
            )}
            {analise.bilhete_multipla && (
              <BilheteMultiplaCard
                pernas={analise.bilhete_multipla.pernas}
                confiancaCombinada={analise.bilhete_multipla.confianca_combinada}
              />
            )}
          </div>
        )}

        {analise.disponivel && analise.resumo && (
          <div className="mt-3 flex items-start justify-center gap-1.5 text-center">
            <p className="text-xs italic leading-relaxed text-muted-foreground">“{analise.resumo}”</p>
            <span className="mt-0.5 shrink-0 rounded-full bg-violet-500/15 px-1.5 py-0.5 text-[8px] font-bold uppercase tracking-wide text-violet-400">
              PRO
            </span>
          </div>
        )}

        <button
          type="button"
          onClick={() => setMercadosAbertos((v) => !v)}
          className="mt-3 flex w-full items-center justify-center gap-1 text-[11px] font-medium uppercase tracking-wide text-muted-foreground transition-colors hover:text-primary"
        >
          <ChevronDown className={`size-3.5 transition-transform ${mercadosAbertos ? "rotate-180" : ""}`} />
          {mercadosAbertos ? "Ocultar todos os mercados" : "Ver todos os mercados"}
        </button>

        {mercadosAbertos && (
          <div className="mt-2 grid gap-4 rounded-lg border border-border bg-card/60 p-3 sm:grid-cols-2 sm:divide-x sm:divide-border">
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
        )}

        <Link
          href={`/analise/${partida.id}`}
          className="mt-3 flex items-center justify-center gap-1 text-[11px] font-medium uppercase tracking-wide text-muted-foreground/70 transition-colors hover:text-primary"
        >
          <ExternalLink className="size-3" />
          Ver página completa
        </Link>
      </CardContent>
    </Card>
  );
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
          Bilhete simples e múltipla sugeridos pra cada confronto, com base nos mercados em que os times vêm
          se destacando.
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
            <CartaoMelhoresPalpites jogos={jogos} />
            {jogos.map((jogo) => (
              <CardPartida key={jogo.partida.id} {...jogo} />
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
