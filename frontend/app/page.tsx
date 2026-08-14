"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button, buttonVariants } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

interface PartidaRodada {
  id: number;
  data: string;
  time_mandante_id: number;
  time_mandante: string;
  time_visitante_id: number;
  time_visitante: string;
  gols_mandante: number;
  gols_visitante: number;
}

interface RodadaResponse {
  rodada: number;
  partidas: PartidaRodada[];
}

interface RodadaAtualResponse {
  rodada_atual: number;
  rodada_maxima: number;
}

function TicketSkeleton() {
  return (
    <Card className="overflow-hidden">
      <CardContent className="py-4">
        <Skeleton className="mx-auto h-3 w-20" />
        <div className="mt-3 flex items-center justify-center gap-3 sm:gap-4">
          <Skeleton className="h-4 flex-1" />
          <Skeleton className="h-6 w-16 shrink-0" />
          <Skeleton className="h-4 flex-1" />
        </div>
      </CardContent>
    </Card>
  );
}

function formatarData(dataStr: string) {
  const partes = dataStr.split("-");
  if (partes.length === 3) {
    const [ano, mes, dia] = partes;
    return `${dia}/${mes}/${ano}`;
  }
  return dataStr;
}

export default function Home() {
  const [rodadaMaxima, setRodadaMaxima] = useState<number | null>(null);
  const [rodadaSelecionada, setRodadaSelecionada] = useState<number | null>(null);
  const [partidas, setPartidas] = useState<PartidaRodada[]>([]);
  const [carregandoInicial, setCarregandoInicial] = useState(true);
  const [carregandoRodada, setCarregandoRodada] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/rodadas/atual")
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

    fetch(`http://127.0.0.1:8000/rodadas/${rodadaSelecionada}`)
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
        <div className="mx-auto max-w-2xl">
          <div>
            <h1 className="font-heading text-2xl font-semibold uppercase tracking-wide sm:text-3xl">
              Football Analytics Platform
            </h1>
            <p className="mt-2 text-sm text-muted-foreground sm:text-base">
              Brasileirão Série A 2026, navegue pelas rodadas.
            </p>
          </div>

          <div className="mt-10 flex items-center justify-center gap-6 sm:gap-10">
            <Button variant="outline" size="icon" disabled aria-label="Rodada anterior">
              <ChevronLeft />
            </Button>
            <div className="text-center">
              <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-muted-foreground">
                Rodada
              </p>
              <Skeleton className="mx-auto mt-1 h-10 w-24" />
            </div>
            <Button variant="outline" size="icon" disabled aria-label="Próxima rodada">
              <ChevronRight />
            </Button>
          </div>

          <div className="mt-8 grid gap-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <TicketSkeleton key={i} />
            ))}
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-background px-4 py-8 text-foreground sm:px-6 sm:py-10">
      <div className="mx-auto max-w-2xl">
        <div className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
          <div>
            <h1 className="font-heading text-2xl font-semibold uppercase tracking-wide sm:text-3xl">
              Football Analytics Platform
            </h1>
            <p className="mt-2 text-sm text-muted-foreground sm:text-base">
              Brasileirão Série A 2026, navegue pelas rodadas.
            </p>
          </div>
          <div className="flex w-full shrink-0 flex-wrap gap-2 sm:w-auto">
            <Link href="/times" className={buttonVariants({ variant: "outline" })}>
              Times
            </Link>
            <Link href="/comparar" className={buttonVariants({ variant: "outline" })}>
              Comparar
            </Link>
            <Link href="/projecao" className={buttonVariants({ variant: "default" })}>
              Projeção
            </Link>
          </div>
        </div>

        <div className="mt-10 flex items-center justify-center gap-6 sm:gap-10">
          <Button
            variant="outline"
            size="icon"
            disabled={rodadaSelecionada <= 1}
            onClick={() => setRodadaSelecionada((r) => (r ?? 1) - 1)}
            aria-label="Rodada anterior"
          >
            <ChevronLeft />
          </Button>

          <div className="text-center">
            <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-muted-foreground">
              Rodada
            </p>
            <p className="font-heading text-4xl font-semibold tabular-nums sm:text-5xl">
              {rodadaSelecionada}
              <span className="text-lg text-muted-foreground sm:text-xl"> / {rodadaMaxima}</span>
            </p>
          </div>

          <Button
            variant="outline"
            size="icon"
            disabled={rodadaSelecionada >= rodadaMaxima}
            onClick={() => setRodadaSelecionada((r) => (r ?? 1) + 1)}
            aria-label="Próxima rodada"
          >
            <ChevronRight />
          </Button>
        </div>

        <div
          className={`mt-8 grid gap-3 transition-opacity duration-200 motion-reduce:transition-none ${carregandoRodada ? "opacity-40" : "opacity-100"}`}
        >
          {carregandoRodada ? (
            Array.from({ length: 4 }).map((_, i) => <TicketSkeleton key={i} />)
          ) : partidas.length === 0 ? (
            <p className="py-8 text-center text-muted-foreground">
              Nenhuma partida cadastrada para essa rodada ainda.
            </p>
          ) : (
            partidas.map((partida) => (
              <Card key={partida.id} className="overflow-hidden">
                <CardContent className="py-4">
                  <p className="text-center text-[11px] uppercase tracking-wide text-muted-foreground">
                    {formatarData(partida.data)}
                  </p>
                  <div className="mt-2 flex items-center justify-center gap-3 sm:gap-4">
                    <Link
                      href={`/times/${partida.time_mandante_id}`}
                      className="min-w-0 flex-1 truncate text-right font-medium transition-colors hover:text-primary"
                    >
                      {partida.time_mandante}
                    </Link>
                    <div className="flex shrink-0 items-center gap-1.5 border-x border-dashed border-border px-3 font-mono text-lg font-semibold tabular-nums text-primary sm:text-xl">
                      <span>{partida.gols_mandante}</span>
                      <span className="text-sm text-muted-foreground">–</span>
                      <span>{partida.gols_visitante}</span>
                    </div>
                    <Link
                      href={`/times/${partida.time_visitante_id}`}
                      className="min-w-0 flex-1 truncate font-medium transition-colors hover:text-primary"
                    >
                      {partida.time_visitante}
                    </Link>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </div>
    </main>
  );
}
