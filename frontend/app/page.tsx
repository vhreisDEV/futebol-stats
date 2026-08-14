"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button, buttonVariants } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

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

  if (carregandoInicial) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background text-muted-foreground">
        <p>Carregando rodada...</p>
      </main>
    );
  }

  if (erro || rodadaSelecionada === null || rodadaMaxima === null) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background text-destructive">
        <p>Erro: {erro ?? "Não foi possível carregar a rodada"}</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-background px-4 py-8 text-foreground sm:px-6 sm:py-10">
      <div className="mx-auto max-w-2xl">
        <div className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
          <div>
            <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
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

        <div className="mt-8 flex items-center justify-between gap-4">
          <Button
            variant="outline"
            size="icon"
            disabled={rodadaSelecionada <= 1}
            onClick={() => setRodadaSelecionada((r) => (r ?? 1) - 1)}
            aria-label="Rodada anterior"
          >
            <ChevronLeft />
          </Button>

          <h2 className="text-lg font-semibold sm:text-xl">
            Rodada {rodadaSelecionada}
            <span className="text-muted-foreground"> / {rodadaMaxima}</span>
          </h2>

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

        <div className="mt-6 grid gap-3">
          {carregandoRodada ? (
            <p className="py-8 text-center text-muted-foreground">Carregando jogos...</p>
          ) : partidas.length === 0 ? (
            <p className="py-8 text-center text-muted-foreground">
              Nenhuma partida cadastrada para essa rodada ainda.
            </p>
          ) : (
            partidas.map((partida) => (
              <Card key={partida.id}>
                <CardContent className="flex flex-col gap-2">
                  <p className="text-xs text-muted-foreground">{formatarData(partida.data)}</p>
                  <div className="flex items-center justify-between gap-3">
                    <Link
                      href={`/times/${partida.time_mandante_id}`}
                      className="min-w-0 flex-1 truncate font-medium hover:underline"
                    >
                      {partida.time_mandante}
                    </Link>
                    <span className="shrink-0 font-semibold tabular-nums">
                      {partida.gols_mandante} x {partida.gols_visitante}
                    </span>
                    <Link
                      href={`/times/${partida.time_visitante_id}`}
                      className="min-w-0 flex-1 truncate text-right font-medium hover:underline"
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
