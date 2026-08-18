"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { VhSpinner } from "@/components/vh-spinner";
import { corTime, iniciais } from "@/lib/times-visual";
import { API_URL } from "@/lib/api";

interface Time {
  id: number;
  nome: string;
}

export default function Times() {
  const [times, setTimes] = useState<Time[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/times/`)
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

        {carregando ? (
          <div className="mt-6 flex min-h-64 items-center justify-center">
            <VhSpinner />
          </div>
        ) : (
          <div className="mt-6 grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
            {times.map((time) => {
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
        )}
      </div>
    </main>
  );
}
