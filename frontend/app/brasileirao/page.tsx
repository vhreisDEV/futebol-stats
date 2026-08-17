"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ChevronLeft, ChevronRight, ChevronDown, Check } from "lucide-react";
import { Button, buttonVariants } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Classificacao } from "@/components/classificacao";
import { PartidaModal } from "@/components/partida-modal";

function CabecalhoCampeonato() {
  return (
    <div>
      <Link
        href="/"
        className="font-heading text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground transition-colors hover:text-primary"
      >
        VEAGA
      </Link>
      <DropdownMenu>
        <DropdownMenuTrigger className="mt-2 flex items-center gap-1.5 font-heading text-2xl font-semibold uppercase tracking-wide transition-colors hover:text-primary sm:text-3xl">
          Brasileirão Série A 2026
          <ChevronDown className="size-5 text-muted-foreground" />
        </DropdownMenuTrigger>
        <DropdownMenuContent>
          <DropdownMenuLabel>Campeonatos</DropdownMenuLabel>
          <DropdownMenuItem className="justify-between gap-4">
            Brasileirão Série A 2026
            <Check className="size-4 text-primary" />
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}

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
    <Card size="sm" className="overflow-hidden ring-0">
      <CardContent className="py-0.5">
        <Skeleton className="mx-auto h-2 w-14" />
        <div className="mt-1 flex items-center justify-center gap-2">
          <Skeleton className="h-3 flex-1" />
          <Skeleton className="h-4 w-10 shrink-0" />
          <Skeleton className="h-3 flex-1" />
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

export default function Brasileirao() {
  const [rodadaMaxima, setRodadaMaxima] = useState<number | null>(null);
  const [rodadaSelecionada, setRodadaSelecionada] = useState<number | null>(null);
  const [partidas, setPartidas] = useState<PartidaRodada[]>([]);
  const [carregandoInicial, setCarregandoInicial] = useState(true);
  const [carregandoRodada, setCarregandoRodada] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [partidaAbertaId, setPartidaAbertaId] = useState<number | null>(null);

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
        <div className="mx-auto max-w-5xl">
          <CabecalhoCampeonato />

          <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="grid gap-1.5">
              {Array.from({ length: 8 }).map((_, i) => (
                <Skeleton key={i} className="h-8 w-full" />
              ))}
            </div>
            <div>
              <div className="flex items-center justify-center gap-4 sm:gap-6">
                <Button variant="outline" size="icon-sm" disabled aria-label="Rodada anterior">
                  <ChevronLeft />
                </Button>
                <div className="text-center">
                  <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-muted-foreground">
                    Rodada
                  </p>
                  <Skeleton className="mx-auto mt-1 h-8 w-20" />
                </div>
                <Button variant="outline" size="icon-sm" disabled aria-label="Próxima rodada">
                  <ChevronRight />
                </Button>
              </div>
              <div className="mt-4 grid gap-1.5">
                {Array.from({ length: 4 }).map((_, i) => (
                  <TicketSkeleton key={i} />
                ))}
              </div>
            </div>
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
            <Link
              href="/previsao"
              className={buttonVariants({ variant: "default" })}
            >
              Previsão de Jogos
            </Link>
            <Link
              href="/comparar"
              className={buttonVariants({
                variant: "outline",
                className:
                  "!border-rose-500/40 !text-rose-400 hover:!bg-rose-500/10 hover:!text-rose-300",
              })}
            >
              Comparar Times
            </Link>
            <Link
              href="/times"
              className={buttonVariants({
                variant: "outline",
                className:
                  "!border-orange-500/40 !text-orange-400 hover:!bg-orange-500/10 hover:!text-orange-300",
              })}
            >
              Times
            </Link>
            <Link href="/jogadores" className={buttonVariants({ variant: "outline" })}>
              Jogadores
            </Link>
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
            <div className="flex items-center justify-center gap-4 sm:gap-6">
              <Button
                variant="outline"
                size="icon-sm"
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
                <p className="font-heading text-2xl font-semibold tabular-nums sm:text-3xl">
                  {rodadaSelecionada}
                  <span className="text-sm text-muted-foreground sm:text-base"> / {rodadaMaxima}</span>
                </p>
              </div>

              <Button
                variant="outline"
                size="icon-sm"
                disabled={rodadaSelecionada >= rodadaMaxima}
                onClick={() => setRodadaSelecionada((r) => (r ?? 1) + 1)}
                aria-label="Próxima rodada"
              >
                <ChevronRight />
              </Button>
            </div>

            <div
              className={`mt-3 grid gap-1 transition-opacity duration-200 motion-reduce:transition-none ${carregandoRodada ? "opacity-40" : "opacity-100"}`}
            >
              {carregandoRodada ? (
                Array.from({ length: 4 }).map((_, i) => <TicketSkeleton key={i} />)
              ) : partidas.length === 0 ? (
                <p className="py-8 text-center text-muted-foreground">
                  Nenhuma partida cadastrada para essa rodada ainda.
                </p>
              ) : (
                partidas.map((partida) => (
                  <Card
                    key={partida.id}
                    size="sm"
                    onClick={() => setPartidaAbertaId(partida.id)}
                    className="cursor-pointer overflow-hidden ring-0 transition-colors hover:bg-muted/50"
                  >
                    <CardContent className="py-0.5">
                      <p className="text-center text-[9px] uppercase tracking-wide text-muted-foreground">
                        {formatarData(partida.data)}
                      </p>
                      <div className="mt-0.5 flex items-center justify-center gap-2">
                        <Link
                          href={`/times/${partida.time_mandante_id}`}
                          onClick={(e) => e.stopPropagation()}
                          className="min-w-0 flex-1 truncate text-right text-sm font-medium transition-colors hover:text-primary"
                        >
                          {partida.time_mandante}
                        </Link>
                        <div className="flex shrink-0 items-center gap-1 font-mono text-sm font-semibold tabular-nums text-primary">
                          <span>{partida.gols_mandante}</span>
                          <span className="text-xs text-muted-foreground">–</span>
                          <span>{partida.gols_visitante}</span>
                        </div>
                        <Link
                          href={`/times/${partida.time_visitante_id}`}
                          onClick={(e) => e.stopPropagation()}
                          className="min-w-0 flex-1 truncate text-sm font-medium transition-colors hover:text-primary"
                        >
                          {partida.time_visitante}
                        </Link>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </section>
        </div>
      </div>

      <PartidaModal partidaId={partidaAbertaId} onClose={() => setPartidaAbertaId(null)} />
    </main>
  );
}
