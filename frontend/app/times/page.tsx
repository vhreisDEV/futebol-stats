"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { buttonVariants } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

interface Time {
  id: number;
  nome: string;
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

  if (carregando) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background text-muted-foreground">
        <p>Carregando times...</p>
      </main>
    );
  }

  if (erro) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background text-destructive">
        <p>Erro: {erro}</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-background px-4 py-8 text-foreground sm:px-6 sm:py-10">
      <div className="mx-auto max-w-2xl">
        <div className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
          <div>
            <h1 className="font-heading text-2xl font-semibold uppercase tracking-wide sm:text-3xl">
              Times
            </h1>
            <p className="mt-2 text-sm text-muted-foreground sm:text-base">
              Selecione um time para ver os últimos jogos e estatísticas.
            </p>
          </div>
          <Link href="/brasileirao" className={buttonVariants({ variant: "outline" })}>
            ← Rodadas
          </Link>
        </div>

        <div className="mt-8 grid gap-3">
          {times.map((time) => (
            <Link key={time.id} href={`/times/${time.id}`} className="group">
              <Card className="transition-colors hover:bg-muted/50">
                <CardContent className="font-medium transition-colors group-hover:text-primary">
                  {time.nome}
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </main>
  );
}
