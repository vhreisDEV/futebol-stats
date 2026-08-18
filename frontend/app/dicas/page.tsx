"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ChevronLeft, ChevronRight, Flame } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { VhSpinner } from "@/components/vh-spinner";
import { API_URL } from "@/lib/api";

interface Destaque {
  stat: string;
  label: string;
  linha: number;
  acertos: number;
  total: number;
  taxa: number;
  sequencia: number[];
  media: number;
}

interface JogoComDestaques {
  partida_id: number;
  data: string | null;
  rodada: number;
  time_mandante_id: number;
  time_mandante: string;
  time_visitante_id: number;
  time_visitante: string;
  destaques_mandante: Destaque[];
  destaques_visitante: Destaque[];
}

interface DestaquesRodadaResponse {
  rodada: number;
  jogos: JogoComDestaques[];
}

interface RodadaAtualResponse {
  rodada_atual: number;
  rodada_maxima: number;
}

function formatarData(dataStr: string | null) {
  if (!dataStr) return "Data a definir";
  const partes = dataStr.split("-");
  if (partes.length === 3) {
    const [ano, mes, dia] = partes;
    return `${dia}/${mes}/${ano}`;
  }
  return dataStr;
}

function ListaDestaques({ time, destaques }: { time: string; destaques: Destaque[] }) {
  if (destaques.length === 0) {
    return (
      <div className="min-w-0 flex-1">
        <p className="truncate text-xs font-semibold uppercase tracking-wide text-muted-foreground">{time}</p>
        <p className="mt-2 text-xs text-muted-foreground/70">Nada que se destaque.</p>
      </div>
    );
  }

  return (
    <div className="min-w-0 flex-1">
      <p className="truncate text-xs font-semibold uppercase tracking-wide text-muted-foreground">{time}</p>
      <ul className="mt-2 grid gap-2">
        {destaques.map((d) => (
          <li key={d.stat} className="rounded-md bg-muted/40 px-3 py-2">
            <p className="text-sm">
              <span className="font-medium text-foreground">{d.label}</span>{" "}
              <span className="text-muted-foreground">
                mais de <span className="font-mono text-primary">{d.linha}</span> em{" "}
                <span className="font-mono font-semibold text-foreground">
                  {d.acertos}/{d.total}
                </span>{" "}
                jogos ({Math.round(d.taxa * 100)}%)
              </span>
            </p>
            <p className="mt-1.5 flex flex-wrap gap-1">
              {d.sequencia
                .slice()
                .reverse()
                .map((v, i) => (
                  <span
                    key={i}
                    className={`rounded px-1.5 py-0.5 font-mono text-[11px] tabular-nums ${
                      v > d.linha ? "bg-primary/15 font-semibold text-primary" : "bg-muted text-muted-foreground/70"
                    }`}
                  >
                    {v}
                  </span>
                ))}
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function Dicas() {
  const [rodadaMaxima, setRodadaMaxima] = useState<number | null>(null);
  const [rodadaSelecionada, setRodadaSelecionada] = useState<number | null>(null);
  const [jogos, setJogos] = useState<JogoComDestaques[]>([]);
  const [carregandoInicial, setCarregandoInicial] = useState(true);
  const [carregandoRodada, setCarregandoRodada] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/rodadas/atual`)
      .then((r) => {
        if (!r.ok) throw new Error("Erro ao buscar a rodada atual");
        return r.json();
      })
      .then((dados: RodadaAtualResponse) => {
        setRodadaMaxima(dados.rodada_maxima);
        setRodadaSelecionada(Math.min(dados.rodada_atual + 1, dados.rodada_maxima));
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

    fetch(`${API_URL}/destaques/rodada/${rodadaSelecionada}`)
      .then((r) => {
        if (r.status === 404) return { rodada: rodadaSelecionada, jogos: [] };
        if (!r.ok) throw new Error("Erro ao buscar destaques da rodada");
        return r.json();
      })
      .then((dados: DestaquesRodadaResponse) => {
        setJogos(dados.jogos);
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
      <main className="flex min-h-screen items-center justify-center bg-background text-foreground">
        <VhSpinner />
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-background px-4 py-8 text-foreground sm:px-6 sm:py-10">
      <div className="mx-auto max-w-3xl">
        <Link
          href="/brasileirao"
          className="inline-flex items-center gap-1 text-xs font-medium uppercase tracking-wide text-muted-foreground transition-colors hover:text-primary"
        >
          <ChevronLeft className="h-3.5 w-3.5" />
          Brasileirão
        </Link>

        <div className="mt-2 flex items-center gap-2">
          <Flame className="size-6 text-emerald-400" />
          <h1 className="font-heading text-2xl font-semibold uppercase tracking-wide sm:text-3xl">
            Dicas da Rodada
          </h1>
        </div>
        <p className="mt-1 text-sm text-muted-foreground">
          Sequências recentes de cada time (escanteios, chutes, cartões) que vêm se repetindo, pros confrontos que
          ainda vão acontecer.
        </p>

        <div className="mx-auto mt-6 flex w-fit items-stretch overflow-hidden rounded-lg border border-border bg-card">
          <button
            type="button"
            disabled={rodadaSelecionada <= 1}
            onClick={() => setRodadaSelecionada((r) => (r ?? 1) - 1)}
            aria-label="Rodada anterior"
            className="flex items-center justify-center px-3 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground disabled:pointer-events-none disabled:opacity-30"
          >
            <ChevronLeft className="size-4" />
          </button>
          <div className="flex flex-col items-center justify-center border-x border-border px-6 py-1.5">
            <span className="text-[10px] font-medium uppercase tracking-[0.2em] text-muted-foreground">Rodada</span>
            <span className="font-mono text-xl font-bold tabular-nums text-primary sm:text-2xl">
              {rodadaSelecionada}
              <span className="text-xs font-normal text-muted-foreground sm:text-sm"> / {rodadaMaxima}</span>
            </span>
          </div>
          <button
            type="button"
            disabled={rodadaSelecionada >= rodadaMaxima}
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
            Nenhuma sequência chamativa encontrada pra essa rodada.
          </div>
        ) : (
          <div className="mt-6 grid gap-3">
            {jogos.map((jogo) => (
              <Card key={jogo.partida_id} className="overflow-hidden">
                <CardContent>
                  <p className="text-center text-xs uppercase tracking-wide text-muted-foreground">
                    {formatarData(jogo.data)}
                  </p>
                  <p className="mt-1 text-center font-heading text-base font-semibold uppercase tracking-wide">
                    {jogo.time_mandante}
                    <span className="mx-2 text-muted-foreground">x</span>
                    {jogo.time_visitante}
                  </p>
                  <div className="mt-4 grid gap-4 sm:grid-cols-2 sm:divide-x sm:divide-border">
                    <ListaDestaques time={jogo.time_mandante} destaques={jogo.destaques_mandante} />
                    <div className="sm:pl-4">
                      <ListaDestaques time={jogo.time_visitante} destaques={jogo.destaques_visitante} />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
