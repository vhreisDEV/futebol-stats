"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

interface Time {
  id: number;
  nome: string;
}

// Cores reais das camisas/escudos de cada time (aproximadas) -- usadas
// como identidade visual provisoria ate termos os escudos de verdade.
const CORES_TIME: Record<string, { fundo: string; borda: string; textoEscuro?: boolean }> = {
  "Athletico-PR": { fundo: "#C8102E", borda: "#000000" },
  "Atlético-MG": { fundo: "#000000", borda: "#FFFFFF" },
  Bahia: { fundo: "#0038A8", borda: "#E4022C" },
  Botafogo: { fundo: "#000000", borda: "#FFFFFF" },
  Chapecoense: { fundo: "#1B7B3A", borda: "#FFFFFF" },
  Corinthians: { fundo: "#000000", borda: "#FFFFFF" },
  Coritiba: { fundo: "#0F7A3D", borda: "#FFFFFF" },
  Cruzeiro: { fundo: "#003DA5", borda: "#FFFFFF" },
  Flamengo: { fundo: "#C8102E", borda: "#000000" },
  Fluminense: { fundo: "#8B1538", borda: "#046A38" },
  Grêmio: { fundo: "#0D80C7", borda: "#000000" },
  Internacional: { fundo: "#E2001A", borda: "#FFFFFF" },
  Mirassol: { fundo: "#FFD400", borda: "#1B7B3A", textoEscuro: true },
  Palmeiras: { fundo: "#006437", borda: "#FFFFFF" },
  "Red Bull Bragantino": { fundo: "#D50032", borda: "#FFFFFF" },
  Remo: { fundo: "#0033A0", borda: "#FFFFFF" },
  Santos: { fundo: "#FFFFFF", borda: "#000000", textoEscuro: true },
  "São Paulo": { fundo: "#C1121C", borda: "#000000" },
  "Vasco da Gama": { fundo: "#000000", borda: "#FFFFFF" },
  Vitória: { fundo: "#C8102E", borda: "#000000" },
};

function corTime(nome: string) {
  return CORES_TIME[nome] ?? { fundo: "#3f3f46", borda: "#71717a" };
}

function iniciais(nome: string) {
  const partes = nome.replace(/-/g, " ").split(" ").filter(Boolean);
  if (partes.length === 1) return partes[0].slice(0, 2).toUpperCase();
  return (partes[0][0] + partes[partes.length - 1][0]).toUpperCase();
}

export default function Times() {
  const [times, setTimes] = useState<Time[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/times/")
      .then((r) => {
        if (!r.ok) throw new Error("Erro ao buscar times");
        return r.json();
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

  if (erro) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background text-destructive">
        <p>Erro: {erro}</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-background px-4 py-8 text-foreground sm:px-6 sm:py-10">
      <div className="mx-auto max-w-3xl">
        <div className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
          <div>
            <Link
              href="/brasileirao"
              className="inline-flex items-center gap-1 text-xs font-medium uppercase tracking-wide text-muted-foreground transition-colors hover:text-primary"
            >
              <ChevronLeft className="h-3.5 w-3.5" />
              Brasileirão
            </Link>
            <h1 className="mt-2 font-heading text-2xl font-semibold uppercase tracking-wide sm:text-3xl">
              Times
            </h1>
            <p className="mt-1 text-sm text-muted-foreground">
              {carregando ? "Carregando…" : `${times.length} times`} · selecione um para ver jogos e estatísticas.
            </p>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {carregando
            ? Array.from({ length: 12 }).map((_, i) => (
                <Card key={i} size="sm" className="ring-0">
                  <CardContent className="flex items-center gap-3">
                    <Skeleton className="size-8 shrink-0 rounded-full" />
                    <Skeleton className="h-4 flex-1" />
                  </CardContent>
                </Card>
              ))
            : times.map((time) => {
                const cores = corTime(time.nome);
                return (
                <Link key={time.id} href={`/times/${time.id}`} className="group">
                  <Card size="sm" className="ring-0 transition-colors hover:bg-muted/50">
                    <CardContent className="flex items-center gap-3">
                      <span
                        className={`flex size-8 shrink-0 items-center justify-center rounded-full border-2 text-xs font-bold ${cores.textoEscuro ? "text-black" : "text-white"}`}
                        style={{ backgroundColor: cores.fundo, borderColor: cores.borda }}
                      >
                        {iniciais(time.nome)}
                      </span>
                      <span className="min-w-0 flex-1 truncate font-medium transition-colors group-hover:text-primary">
                        {time.nome}
                      </span>
                      <ChevronRight className="size-4 shrink-0 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100" />
                    </CardContent>
                  </Card>
                </Link>
                );
              })}
        </div>
      </div>
    </main>
  );
}
