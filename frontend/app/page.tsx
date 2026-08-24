"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ChevronRight, Trophy } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { LightRays } from "@/components/light-rays";
import { SpotlightCard } from "@/components/spotlight-card";
import { API_URL, CAMPEONATO_BRASILEIRAO_ID } from "@/lib/api";

interface RodadaAtualResponse {
  rodada_atual: number;
  rodada_maxima: number;
}

export default function Home() {
  const [rodada, setRodada] = useState<RodadaAtualResponse | null>(null);
  const [totalTimes, setTotalTimes] = useState<number | null>(null);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    Promise.allSettled([
      fetch(`${API_URL}/rodadas/atual?campeonato_id=${CAMPEONATO_BRASILEIRAO_ID}`).then((r) => (r.ok ? r.json() : null)),
      fetch(`${API_URL}/times/?campeonato_id=${CAMPEONATO_BRASILEIRAO_ID}`).then((r) => (r.ok ? r.json() : [])),
    ]).then(([resultadoRodada, resultadoTimes]) => {
      if (resultadoRodada.status === "fulfilled") setRodada(resultadoRodada.value);
      if (resultadoTimes.status === "fulfilled" && Array.isArray(resultadoTimes.value)) {
        setTotalTimes(resultadoTimes.value.length);
      }
      setCarregando(false);
    });
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

      <div className="animate-in fade-in zoom-in-95 relative w-full max-w-sm text-center duration-700">
        <h1 className="text-shimmer-gold font-heading text-5xl font-semibold uppercase tracking-wide sm:text-6xl">
          VEAGA
        </h1>
        <p className="mt-2 text-xs uppercase tracking-[0.3em] text-primary sm:text-sm">
          Football Data &amp; Analytics
        </p>

        <Link href="/brasileirao" className="group mt-10 block">
          <SpotlightCard spotlightColor="rgba(212, 175, 55, 0.35)">
            <Card className="overflow-hidden border-primary/20 text-left transition-colors hover:border-primary/50">
              <CardContent className="flex items-center gap-3">
                <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
                  <Trophy className="size-4" />
                </span>
                <div className="min-w-0 flex-1">
                  <p className="font-medium">Brasileirão Série A 2026</p>
                  {carregando ? (
                    <span className="mt-1 block h-3 w-28 shimmer-bar-gold" />
                  ) : rodada || totalTimes !== null ? (
                    <p className="mt-0.5 font-mono text-[11px] tabular-nums text-muted-foreground">
                      {rodada && `Rodada ${rodada.rodada_atual}/${rodada.rodada_maxima}`}
                      {rodada && totalTimes !== null && " · "}
                      {totalTimes !== null && `${totalTimes} times`}
                    </p>
                  ) : null}
                </div>
                <ChevronRight className="size-4 shrink-0 text-primary transition-transform group-hover:translate-x-0.5" />
              </CardContent>
            </Card>
          </SpotlightCard>
        </Link>
      </div>
    </main>
  );
}
