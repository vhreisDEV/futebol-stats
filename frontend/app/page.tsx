"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ChevronRight, Trophy } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { LightRays } from "@/components/light-rays";
import { SpotlightCard } from "@/components/spotlight-card";
import { API_URL, CAMPEONATO_BRASILEIRAO_ID } from "@/lib/api";
import { flagSrcQuadrada } from "@/lib/paises";

interface Campeonato {
  id: number;
  nome: string;
  pais_nome: string;
  pais_codigo: string;
  temporada: number;
  rodadas_total: number | null;
  rodada_atual: number | null;
  total_times: number;
}

export default function Home() {
  const [campeonatos, setCampeonatos] = useState<Campeonato[]>([]);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/campeonatos/`)
      .then((r) => (r.ok ? r.json() : { campeonatos: [] }))
      .then((dados: { campeonatos: Campeonato[] }) => {
        setCampeonatos(dados.campeonatos);
        setCarregando(false);
      })
      .catch(() => setCarregando(false));
  }, []);

  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-background px-4 py-8 text-foreground">
      <div aria-hidden className="pointer-events-none absolute inset-0 opacity-40">
        <LightRays
          raysOrigin="top-center"
          raysColor="#d4af37"
          raysSpeed={1.1}
          lightSpread={0.6}
          rayLength={1.0}
          fadeDistance={0.9}
          saturation={0.7}
          followMouse
          mouseInfluence={0.08}
          noiseAmount={0.05}
          distortion={0.05}
        />
      </div>
      <div
        aria-hidden
        className="pointer-events-none absolute left-1/2 top-0 h-72 w-72 -translate-x-1/2 -translate-y-1/3 rounded-full bg-primary/20 blur-[100px]"
      />

      <div className="animate-in fade-in zoom-in-95 relative w-full max-w-md text-center duration-700">
        <h1 className="text-shimmer-gold font-heading text-5xl font-semibold uppercase tracking-wide sm:text-6xl">
          VEAGA
        </h1>
        <p className="mt-2 text-xs uppercase tracking-[0.3em] text-primary sm:text-sm">
          Football Data &amp; Analytics
        </p>

        <div className="mt-10 grid gap-3 text-left">
          {carregando ? (
            <div className="flex items-center gap-3 rounded-lg border border-primary/20 bg-card px-4 py-3.5">
              <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
                <Trophy className="size-4" />
              </span>
              <span className="block h-3 w-28 shimmer-bar-gold" />
            </div>
          ) : (
            campeonatos.map((c) => (
              <Link
                key={c.id}
                href={c.id === CAMPEONATO_BRASILEIRAO_ID ? "/brasileirao" : `/campeonato/${c.id}`}
                className="group block"
              >
                <SpotlightCard spotlightColor="rgba(212, 175, 55, 0.35)">
                  <Card className="overflow-hidden border-primary/20 text-left transition-colors hover:border-primary/50">
                    <CardContent className="flex items-center gap-3">
                      <span className="flex size-9 shrink-0 items-center justify-center overflow-hidden rounded-full bg-primary/10">
                        {/* eslint-disable-next-line @next/next/no-img-element -- SVG local, decorativo, sem necessidade de otimizacao do Next/Image */}
                        <img src={flagSrcQuadrada(c.pais_codigo)} alt="" className="size-full object-cover" />
                      </span>
                      <div className="min-w-0 flex-1">
                        <p className="truncate font-medium">
                          {c.nome} {c.temporada}
                        </p>
                        <p className="mt-0.5 font-mono text-[11px] tabular-nums text-muted-foreground">
                          {c.rodada_atual && `Rodada ${c.rodada_atual}/${c.rodadas_total ?? "?"}`}
                          {c.rodada_atual && " · "}
                          {c.total_times} times
                        </p>
                      </div>
                      <ChevronRight className="size-4 shrink-0 text-primary transition-transform group-hover:translate-x-0.5" />
                    </CardContent>
                  </Card>
                </SpotlightCard>
              </Link>
            ))
          )}
        </div>
      </div>
    </main>
  );
}
